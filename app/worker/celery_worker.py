from celery import Celery

celery_app = Celery(
    "document_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# IMPORTANT: load task modules
celery_app.conf.imports = (
    "app.tasks.document_tasks",
)