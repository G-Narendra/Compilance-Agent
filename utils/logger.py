"""
utils/logger.py - structured logging with structlog.

i'm using structlog because it's way better than the standard logging module
for production apps. you get structured json logs that are easy to search
and filter in your log aggregator.
"""

import sys
import structlog
from config import get_settings


def setup_logging():
    """configure structured logging for the whole app."""
    settings = get_settings()

    # pick processors based on whether we're in debug mode
    if settings.debug:
        processors = [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            *processors,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "compliance_agent"):
    """
    get a named logger. use this everywhere instead of print().

    usage:
        log = get_logger("my_module")
        log.info("something happened", doc_id="abc123", framework="gdpr")
    """
    return structlog.get_logger(name)
