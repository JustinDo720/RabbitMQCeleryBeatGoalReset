from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from django.core.management import call_command

@shared_task
def add(x,y):
    return x+y

@shared_task
def doubled(x):
    return x*2

@shared_task
def check_goal_task(duration):
    call_command('check_goal', duration=duration)    