import json
import logging
from logging import Logger, LogRecord


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
            log_record["user_ip"] = record.user_ip
        if hasattr(record, "user_agent"):
            log_record["user_agent"] = record.user_agent
        if hasattr(record, "current_user"):
            log_record["current_user"] = record.current_user
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "method"):
            log_record["method"] = record.method
        

        return json.dumps(log_record)


def create_logger(logger_name: str = __name__) -> Logger:
    """
    Create a logger for the module  
  
    Args:  
        logger_name: The name of the logger  
  
    Returns:  
        The logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()

    formatter = DictFormatter()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
