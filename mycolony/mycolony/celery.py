import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycolony.settings')

app = Celery('mycolony')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
