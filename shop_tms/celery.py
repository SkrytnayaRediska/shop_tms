import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_tms.settings')


BASE_REDIS_URL = os.environ.get('REDIS_URL', settings.CELERY_BROKER_URL)

app = Celery('shop_tms')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.broker_url = BASE_REDIS_URL


