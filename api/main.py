"""api/main.py — FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import articles, search, stats, trigger
from core.config import get_settings


def _configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog for the API process."""
    import logging
    import sys

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: configure logging on startup."""
    settings = get_settings()
    _configure_logging(settings.log_level)
    logger = structlog.get_logger("api.startup")
    logger.info(
        "api.startup",
        host=settings.api_host,
        port=settings.api_port,
        frontend_origin=settings.frontend_origin,
        log_level=settings.log_level,
    )
    yield
    logger.info("api.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Davision AI Tech & Trend Radar API",
        description=(
            "Autonomous multi-agent intelligence platform for AI/ML research discovery. "
            "Powered by Scout, Analyzer, and Dispatcher agents."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS — allow Next.js frontend ────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(articles.router, prefix="/api", tags=["Articles"])
    app.include_router(search.router, prefix="/api", tags=["Search"])
    app.include_router(stats.router, prefix="/api", tags=["Stats"])
    app.include_router(trigger.router, prefix="/api", tags=["Pipeline"])

    @app.get("/api/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()

