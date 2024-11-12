from __future__ import absolute_import, unicode_literals
import os 
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jb_goal.settings')

# Making the celery instance 
app = Celery('jb_goal') # name of project
app.config_from_object(settings, namespace='CELERY')
app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'
app.autodiscover_tasks()