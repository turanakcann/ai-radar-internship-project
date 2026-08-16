"""api/routes/trigger.py — Manual pipeline trigger endpoint."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException

from core.schemas import RunTriggerResponse

router = APIRouter()

# Track if a pipeline is already running
_pipeline_running = False


@router.post("/run", response_model=RunTriggerResponse)
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    Manually trigger the full Scout → Analyzer → Dispatcher pipeline.

    Useful for testing and on-demand refreshes.
    Returns immediately with a run_id; pipeline executes in background.
    """
    global _pipeline_running

    if _pipeline_running:
        raise HTTPException(
            status_code=409,
            detail="A pipeline run is already in progress. Please wait.",
        )

    async def run_in_background():
        global _pipeline_running
        _pipeline_running = True
        try:
            from agents.orchestrator import run_pipeline
            await run_pipeline()
        finally:
            _pipeline_running = False

    background_tasks.add_task(run_in_background)

    import uuid
    run_id = uuid.uuid4().hex

    return RunTriggerResponse(
        run_id=run_id,
        status="started",
        message="Pipeline triggered. Monitor /api/stats for progress.",
    )


@router.get("/run/status")
async def pipeline_status():
    """Check if a pipeline is currently running."""
    return {"running": _pipeline_running}
