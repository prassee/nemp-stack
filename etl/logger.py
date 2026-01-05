"""
Centralized logging configuration for ETL pipeline.

Provides unified logging across all modules with:
- Console output (INFO level and above)
- File output to ./logs/etl.log (DEBUG level and above)
- Consistent timestamp and format across all messages
"""

import logging
from pathlib import Path


def setup_logging():
    """Initialize logging with console and file handlers."""
    # Create logs directory
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger configuration
    root_logger = logging.getLogger("etl")
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers (avoid duplicates)
    root_logger.handlers = []
    
    # Console handler (INFO level - user-facing output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (DEBUG level - detailed logging for troubleshooting)
    file_handler = logging.FileHandler(log_dir / "etl.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name):
    """Get a logger instance for a module."""
    return logging.getLogger(f"etl.{name}")
