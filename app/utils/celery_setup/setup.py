from celery import Celery

from app.core.config import settings


def make_celery(app=None, broker_url=None, result_backend=None):
    """
    Sets up Celery.
    """
    name = "app.utils.celery_setup.setup"
    if app:
        name = app.__name__
    if not broker_url and not result_backend:
        if settings.mode == "TEST":
            broker_url = settings.celery_broker_url_test
            result_backend = settings.celery_result_backend_test

    # Set up Celery with custom broker and result backend
    celery = Celery(
        name,
        broker=broker_url or settings.celery_broker_url,
        backend=result_backend or settings.celery_result_backend,
    )

    # add celery configurations
    celery.config_from_object("app.core.celery_config")

    # Automatically discover tasks from the specified module
    celery.autodiscover_tasks(["app.utils.celery_setup.tasks"], related_name="tasks")

    return celery


# Create a Celery app instance for production
app = make_celery()

if __name__ == "__main__":

    app.start()
