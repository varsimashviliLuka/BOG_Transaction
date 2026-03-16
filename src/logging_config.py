import logging
import os
from logging.handlers import RotatingFileHandler

# Resolves to ./logs/ from project root regardless of where script is called
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')


def get_logger(name: str, log_filename: str = None, level=logging.INFO) -> logging.Logger:
    """
    Returns a named logger writing to ./logs/<log_filename>.
    Safe to call multiple times — won't add duplicate handlers.

    Usage:
        logger = get_logger('outsidescript')
        logger = get_logger('authenticate', level=logging.INFO)
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_filename = log_filename or f"{name}.log"
    log_path = os.path.join(LOGS_DIR, log_filename)

    logger = logging.getLogger(name)

    if logger.handlers:  # Already configured, return as-is
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)-8s %(name)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rotate at 5MB, keep last 5 files → outsidescript.log, outsidescript.log.1 ... .5
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    logger.addHandler(file_handler)

    return logger