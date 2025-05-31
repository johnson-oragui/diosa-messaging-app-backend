import json
import logging
from logging import Logger, LogRecord
from logging.handlers import RotatingFileHandler


class DictFormatter(logging.Formatter):
    """
    Custom formatter to output logs as a dictionary (JSON-like structure).
    """

    def format(self, record: LogRecord) -> str:
        """
        Changes format to a dictionary type
        """
        log_record = {
            "time": self.formatTime(record=record, datefmt=self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }

        if hasattr(record, "user_ip"):
            log_record["user_ip"] = record.user_ip  # type: ignore
        if hasattr(record, "user_agent"):
            log_record["user_agent"] = record.user_agent  # type: ignore
        if hasattr(record, "current_user"):
            log_record["current_user"] = record.current_user  # type: ignore
        if hasattr(record, "path"):
            log_record["path"] = record.path  # type: ignore
        if hasattr(record, "method"):
            log_record["method"] = record.method  # type: ignore
        if hasattr(record, "payload"):
            log_record["payload"] = record.payload  # type: ignore
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code  # type: ignore
        if hasattr(record, "process_time"):
            log_record["process_time"] = record.process_time  # type: ignore

        return json.dumps(log_record)


def create_logger(
    logger_name: str = __name__,
    log_file: str = "logs/app.log",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 10,
) -> Logger:
    """
    Create a logger for the module

    Args:
        logger_name: The name of the logger
        log_file: The name of the log file
        max_bytes: Maximum size of the log file before rotation (in bytes)
        backup_count: Number of backup files to keep

    Returns:
        The logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Use the DictFormatter
    formatter = DictFormatter()

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )

    file_handler.setFormatter(formatter)
    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # console handler for logs in the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
