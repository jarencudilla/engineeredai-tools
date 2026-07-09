"""
logging_setup.py

Configures logging for the whole backend. Called once at startup from
main.py. Every other module just does `import logging; logging.getLogger(__name__)`
and inherits this config.

Depends on: nothing.
Called from: main.py
"""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """
    configure_logging
    Sets up a single consistent log format for the whole app, printed
    to stdout so it's visible whether running via terminal or packaged exe.
    @param  level  int  Logging level, defaults to INFO.
    @return None
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )

    # Quiet down noisy third-party loggers so our own logs aren't buried.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
