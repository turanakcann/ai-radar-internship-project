"""
agents/orchestrator.py — Master Orchestrator Agent.

Coordinates the Scout → Analyzer → Dispatcher pipeline on a cron schedule
(every N hours via APScheduler) or via manual HTTP trigger.

Guarantees:
- Sequential phase execution (Scout must succeed before Analyzer is invoked).
- Error isolation: one failed phase is logged without crashing the scheduler.
- Each run is audit-logged in the `run_logs` PostgreSQL table.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from agents.analyzer_agent import run_analyzer
from agents.dispatcher_agent import run_dispatcher
from agents.scout_agent import run_scout
from core.config import get_settings
from core.database import get_session
from core.models import RunLog

logger = structlog.get_logger(__name__)


async def _log_run(
    run_id: str,
    phase: str,
    status: str,
    articles_found: int = 0,
    articles_saved: int = 0,
    error_message: str | None = None,
    started_at: datetime | None = None,
) -> None:
    """Insert a run audit log entry into PostgreSQL."""
    async with get_session() as session:
        log = RunLog(
            run_id=run_id,
            phase=phase,
            status=status,
            articles_found=articles_found,
            articles_saved=articles_saved,
            error_message=error_message,
            started_at=started_at or datetime.now(tz=timezone.utc),
            finished_at=datetime.now(tz=timezone.utc),
        )
        session.add(log)


async def run_pipeline() -> dict:
    """
    Execute the full Scout → Analyzer → Dispatcher pipeline.

    Returns a summary dict with counts for each phase.
    """
    run_id = uuid.uuid4().hex
    pipeline_start = datetime.now(tz=timezone.utc)
    logger.info("orchestrator.pipeline_start", run_id=run_id)

    summary = {
        "run_id": run_id,
        "scout_count": 0,
        "analyzer_count": 0,
        "dispatched_count": 0,
        "errors": [],
    }

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 1: Scout Agent
    # ─────────────────────────────────────────────────────────────────────────
    scout_start = datetime.now(tz=timezone.utc)
    try:
        scout_results = await run_scout()
        summary["scout_count"] = len(scout_results)
        await _log_run(
            run_id=run_id,
            phase="scout",
            status="success",
            articles_found=len(scout_results),
            articles_saved=len(scout_results),
            started_at=scout_start,
        )
        logger.info("orchestrator.scout_done", count=len(scout_results))
    except Exception as exc:
        error_msg = f"Scout failed: {exc}"
        summary["errors"].append(error_msg)
        await _log_run(
            run_id=run_id,
            phase="scout",
            status="error",
            error_message=error_msg,
            started_at=scout_start,
        )
        logger.error("orchestrator.scout_failed", error=str(exc))
        # Scout failure is fatal — cannot proceed without data
        return summary

    if not scout_results:
        logger.info("orchestrator.no_new_items")
        return summary

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 2: Analyzer Agent
    # ─────────────────────────────────────────────────────────────────────────
    analyzer_start = datetime.now(tz=timezone.utc)
    try:
        analyzer_results = await run_analyzer(scout_results)
        summary["analyzer_count"] = len(analyzer_results)
        await _log_run(
            run_id=run_id,
            phase="analyze",
            status="success",
            articles_found=len(scout_results),
            articles_saved=len(analyzer_results),
            started_at=analyzer_start,
        )
        logger.info("orchestrator.analyzer_done", count=len(analyzer_results))
    except Exception as exc:
        error_msg = f"Analyzer failed: {exc}"
        summary["errors"].append(error_msg)
        await _log_run(
            run_id=run_id,
            phase="analyze",
            status="error",
            error_message=error_msg,
            started_at=analyzer_start,
        )
        logger.error("orchestrator.analyzer_failed", error=str(exc))
        # Analyzer failure doesn't prevent dispatching previously stored items
        analyzer_results = []

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 3: Dispatcher Agent
    # ─────────────────────────────────────────────────────────────────────────
    dispatch_start = datetime.now(tz=timezone.utc)
    try:
        dispatch_results = await run_dispatcher()
        dispatched = sum(1 for r in dispatch_results if r.success)
        summary["dispatched_count"] = dispatched
        await _log_run(
            run_id=run_id,
            phase="dispatch",
            status="success",
            articles_saved=dispatched,
            started_at=dispatch_start,
        )
        logger.info("orchestrator.dispatcher_done", dispatched=dispatched)
    except Exception as exc:
        error_msg = f"Dispatcher failed: {exc}"
        summary["errors"].append(error_msg)
        await _log_run(
            run_id=run_id,
            phase="dispatch",
            status="error",
            error_message=error_msg,
            started_at=dispatch_start,
        )
        logger.error("orchestrator.dispatcher_failed", error=str(exc))

    elapsed = (datetime.now(tz=timezone.utc) - pipeline_start).total_seconds()
    logger.info(
        "orchestrator.pipeline_complete",
        run_id=run_id,
        elapsed_seconds=elapsed,
        **{k: v for k, v in summary.items() if k != "run_id"},
    )
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Scheduler Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    """Start the APScheduler and run pipeline on schedule."""
    import structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
    )

    settings = get_settings()
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(hours=settings.schedule_interval_hours),
        id="tech_radar_pipeline",
        name="Tech Radar Full Pipeline",
        max_instances=1,               # Prevent overlapping runs
        misfire_grace_time=300,        # 5 min grace window
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "orchestrator.scheduler_started",
        interval_hours=settings.schedule_interval_hours,
    )

    # Run immediately on startup
    logger.info("orchestrator.initial_run_start")
    await run_pipeline()

    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("orchestrator.shutdown")


if __name__ == "__main__":
    asyncio.run(main())
