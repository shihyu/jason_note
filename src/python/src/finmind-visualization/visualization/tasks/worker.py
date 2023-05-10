from celery import Celery
from loguru import logger

from visualization.config import (
    MESSAGE_QUEUE_DB,
    MESSAGE_QUEUE_HOST,
    MESSAGE_QUEUE_PASSWORD,
    MESSAGE_QUEUE_PORT,
    MESSAGE_QUEUE_TYPE,
    MESSAGE_QUEUE_USER,
)

if MESSAGE_QUEUE_TYPE == "pyamqp":
    broker = (
        f"pyamqp://{MESSAGE_QUEUE_USER}:{MESSAGE_QUEUE_PASSWORD}@"
        f"{MESSAGE_QUEUE_HOST}:{MESSAGE_QUEUE_PORT}/"
    )
elif MESSAGE_QUEUE_TYPE == "redis":
    broker = (
        f"redis://:{MESSAGE_QUEUE_PASSWORD}@{MESSAGE_QUEUE_HOST}:"
        f"{MESSAGE_QUEUE_PORT}/{MESSAGE_QUEUE_DB}"
    )

logger.info(broker)
app = Celery("task", include="visualization.tasks.task", broker=broker)
