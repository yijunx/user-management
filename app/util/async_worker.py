from celery import Celery
from app.config.app_config import conf
from enum import Enum


celery = Celery(conf.CELERY_SERVICE_NAME, broker=conf.CELERY_BROKER)


class CeleryTaskEnum(str, Enum):
    email_confirmation = "email_confirmation"
    password_reset = "password_reset"
