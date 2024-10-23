
import os
from celery.signals import setup_logging
import logging
from logging.handlers import RotatingFileHandler

# from app.core.config import settings


print("initializing celery config...")
# if not settings.test:
#     result_backend = f"db+{settings.db_url_sync}"
# else:
#     result_backend = f"db+{settings.db_url_test}"

# broker_url = settings.celery_broker_url


result_expire = 3600

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True
task_remote_tracebacks = True
task_default_rate_limit = "100/m"


task_track_started = True

worker_hijack_root_logger = False


info_log_file = "logs/celery_info.log"
error_log_file = "logs/celery_error.log"

os.makedirs('logs', exist_ok=True)

# Ensure Celery uses these loggers
worker_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
worker_task_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@setup_logging.connect
def setup_celerey_logging(**kwargs):
    """
    Sets up logging for celery.
    """
    # Create loggers
    info_logger = logging.getLogger("celery_info")
    error_logger = logging.getLogger("celery_error")

    # Set the logging level
    info_logger.setLevel(logging.INFO)
    error_logger.setLevel(logging.ERROR)

    # Create handlers
    info_handler = RotatingFileHandler(info_log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10MB file size limit
    error_handler = RotatingFileHandler(error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5)

    # Set logging level for handlers
    info_handler.setLevel(logging.INFO)
    error_handler.setLevel(logging.ERROR)

    # Create formatters and add them to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # Add handlers to loggers
    info_logger.addHandler(info_handler)
    error_logger.addHandler(error_handler)

    # Add the custom loggers to the root logger
    logging.getLogger().addHandler(info_handler)
    logging.getLogger().addHandler(error_handler)
