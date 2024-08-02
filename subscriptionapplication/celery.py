"""CELERY Configruation using CLEREY for asynchronous task when the subscription billing period it should automatically 
  deducted money from user for celery using tasks.py celery settings mentioned in settings.py install redis  is required  """
from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE','subscriptionapplication.settings')
app=Celery("subscriptionapplication")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab
minute = 30
hour = 14
day_of_month = 31
month_of_year = 8

app.conf.beat_schedule = {
    'check-due-subscriptions-on-specific-date': {
        'task': 'subscription.tasks.check_due_subscriptions',
        'schedule': crontab(minute=minute, hour=hour, day_of_month=day_of_month, month_of_year=month_of_year),
    },
}



