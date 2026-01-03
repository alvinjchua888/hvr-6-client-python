"""
Logging configuration for the HVR 6.0 Client application

Provides structured logging with file and console output.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logger(
    name: str = "hvr6-client-python",
    level: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Setup and configure logger

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)

    Returns:
        Configured logger instance
    """
    # Get configuration from environment
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_format_type = log_format or os.getenv("LOG_FORMAT", "text").lower()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Define log format
    if log_format_type == "json":
        log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        log_fmt = "%(asctime)s [%(levelname)s] : %(message)s"

    formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / "combined.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # File handler for errors only
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger


# Create default logger instance
logger = setup_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Optional logger name, defaults to main logger

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"hvr6-client-python.{name}")
    return logger
