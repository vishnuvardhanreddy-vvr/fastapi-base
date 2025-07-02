
"""
Logging Setup Module

This module provides a function `setup_logging` that configures both console 
and rotating file logging based on environment variables. 
It supports configurable log levels and optional info-level logging to file.
"""


import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Set up logging for the application.

    This function configures the root logger with:
    - A console handler that logs messages according to the LOG_LEVEL environment variable.
    - A rotating file handler that logs messages based on LOG_INFO_TO_LOGS_FILE and LOG_FILE.

    Environment Variables:
        LOG_LEVEL (str): The log level for console output (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                         Defaults to INFO.
        LOG_INFO_TO_LOGS_FILE (str): If "true"/"1"/"yes", includes WARNING level in file logs.
                                     Otherwise, logs only ERROR and CRITICAL to file.
        LOG_FILE (str): Path to the log file. Defaults to 'app_logs.log'.

    Returns:
        logging.Logger: The configured root logger.
    """

    # Get the log level from the environment variable, default to 'INFO'
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Validate log level
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        log_level = 'INFO'

    # Control log level for file handler
    log_info_to_file = os.getenv(
        "LOG_INFO_TO_LOGS_FILE", "False").lower() in ("true", "1", "yes")
    log_file = os.getenv("LOG_FILE", "app_logs.log")

    # Remove existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up the main logger
    local_logger = logging.getLogger()

    # Set up rotating file handler
    file_handler = RotatingFileHandler(log_file)

    # Set log level for file handler
    if log_info_to_file:
        # includes WARNING, ERROR, CRITICAL
        file_handler.setLevel(logging.WARNING)
    else:
        file_handler.setLevel(logging.ERROR)    # includes only ERROR, CRITICAL

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
        if log_info_to_file else
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    local_logger.addHandler(file_handler)

    # Console handler (show everything from log_level and up)
    console_handler = logging.StreamHandler()
    if log_level == "DEBUG":
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    local_logger.addHandler(console_handler)

    # Set root logger level
    local_logger.setLevel(log_level)

    # One-time message
    local_logger.info("Logging setup complete with level '%s'.", log_level)

    return local_logger


logger = setup_logging()
