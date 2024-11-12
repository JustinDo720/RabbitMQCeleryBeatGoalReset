# Scheduled Goal Reset

## Table of Contents:
   - [Using this project?](#using-this-example-project)
   - [Overview](#overview)
   - [Pre-Req](#pre-req)
   - **Steps**
      - [Setting up Celery.py](#setting-up-celerypy)
      - [Discoverable Task](#making-sure-tasks-are-discovered)
      - [Making Tasks](#creating-our-tasks)
      - [Adding Tasks to Settings](#adding-this-task-as-a-periodic-task)
      - [Setting and Starting Celery Beat](#set-up-and-starting-celery-beat)
   - [Possible Fix with Flower Errors](#fix-flower)
---

## Overview
We're practicing how to integrate **Django Celery & Celery Beat** into our application. This is more of a higher level view on how things works. The client sends a **post request** to our **django server** which sends a **async task** to our **broker: RabbitMQ** (some people use redis or aws). 

**RabbitMQ** runs seperately waiting for tasks in the queue. **Celery** is what sends that task over. We could view those celery tasks with **Flower**. Since we want this to be a **CRON job** which means its a **scheduled/periodic task** we'll be using **Celery Beat**.

---

## Pre-req

You need the **"Quad Stack"**:
 - `pip install celery`
 - `pip install flower`
 - `pip install django-celery-beat`
 - RabbitMQ we'll pull from a **Docker Image**

 Let's pull RabbitMQ (Make sure your Docker Desktop is working):
 - `docker pull rabbitmq:3-management`
 - `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`

 Now that your RabbitMQ is running let's run the rest of our **stack** (Replace jb_goal with your Project Name)
 - Running Celery :
    - `celery -A jb_goal worker -l info --pool=solo`
 - Running Flower: 
    - `celery flower -A jg_goal –port:5555`

Let's hold off **Celery Beat** until we finish creating everything

---

## **Setting up Celery.py**

- Create a **[celery.py](jb_goal/celery.py)** in your **project root** (where **settings.py** is)

Our **Imports**

Important: We need to **import settings**

```python
from __future__ import absolute_import, unicode_literals
import os 
from celery import Celery
from django.conf import settings
```

Telling celery to use the **Django Settings**

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jb_goal.settings')
```

Creating the Celery Instance

```python
app = Celery('jb_goal') # name of project
```

Adding the configs from settings and making sure it auto detects tasks 

```python
app.config_from_object(settings, namespace='CELERY')
app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'
app.autodiscover_tasks()
```

---

## **Making Sure Tasks Are Discovered**

If the tasks aren't showing on your **Dashboard/Flower** it's because we haven't added celery to `__init__py`

In your **project_name/__init__.py/** we need to add our **celery instance**:

[jb_goal/__init__.py](jb_goal/__init__.py)

`from .celery import app`

---

## **Creating our tasks**

In our app (for me it's **jb_goal_app**) we create a **tasks.py**

[jb_goal_app/tasks.py/](jb_goal_app/tasks.py)

Our imports:

```python
from __future__ import absolute_import, unicode_literals
from celery import shared_task
# Calling our Django Management Commands 
# py manage.py check_goals.py
from django.core.management import call_command
```

Creating a task with the `@shared_task` decorator for our celery instance to pick up as a **task**

```python
@shared_task
def check_goal_task(duration):
   # Again we're using call_command to run something like:
   # py manage.py check_goal -d 'Daily'
   call_command('check_goal.py', duration=duration)    
```

---

## **Adding this task as a "Periodic Task"**

In [jb_goal/settings.py](jb_goal/settings.py), we add the schduled task:

Importing in our cron dates 
```python
from celery.schedules import crontab
```

Quick Guide on some `crontab` possibilities:
```python

crontab() # Execute every minute.

crontab(minute=0, hour=0) # Execute daily at midnight.

crontab(minute=0, hour='*/3') # Execute every three hours: midnight, 3am, 6am, 9am, noon, 3pm, 6pm, 9pm.

crontab(minute=0, hour='0,3,6,9,12,15,18,21') # Same as previous.

crontab(minute='*/15') # Execute every 15 minutes.

crontab(day_of_week='sunday') # Execute every minute (!) at Sundays.

crontab(minute='*', hour='*', day_of_week='sun') # Same as previous.

crontab(minute='*/10', hour='3,17,22', day_of_week='thu,fri') # Execute every ten minutes, but only between 3-4 am, 5-6 pm, and 10-11 pm on Thursdays or Fridays.

crontab(minute=0, hour='*/2,*/3') # Execute every even hour, and every hour divisible by three. This means: at every hour except: 1am, 5am, 7am, 11am, 1pm, 5pm, 7pm, 11pm

crontab(minute=0, hour='*/5') # Execute hour divisible by 5. This means that it is triggered at 3pm, not 5pm (since 3pm equals the 24-hour clock value of “15”, which is divisible by 5).

crontab(minute=0, hour='*/3,8-17') # Execute every hour divisible by 3, and every hour during office hours (8am-5pm).

crontab(0, 0, day_of_month='2') # Execute on the second day of every month.

crontab(0, 0, day_of_month='2-30/2') # Execute on every even numbered day.

crontab(0, 0, day_of_month='1-7,15-21') # Execute on the first and third weeks of the month.

crontab(0, 0, day_of_month='11', month_of_year='5') # Execute on the eleventh of May every year.

crontab(0, 0, month_of_year='*/3') # Execute every day on the first month of every quarter.

```

We'll use this knowledge when creating our schdules:
1) Include the name of our **schedueld task** (e.g "reset-daily-goals")
1) Add in your specific task: `app_name.tasks.task_name` 
1) Schedule is where we use crontab for the **frequency**
1) Args is any arguments that the function may have

```python

CELERY_BEAT_SCHEDULE = {
    'reset-daily-goals': {
        'task': 'jb_goal_app.tasks.check_goal_task',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
        'args': ('daily',),
    },
    'reset-weekly-goals': {
        'task': 'jb_goal_app.tasks.check_goal_task',
        'schedule': crontab(day_of_week=0, hour=0, minute=0),  # Run weekly on Sunday at midnight
        'args': ('weekly',),
    },
    'reset-monthly-goals': {
        'task': 'jb_goal_app.tasks.check_goal_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run monthly on the first day of each month at midnight
        'args': ('monthly',),
    },
    'reset-yearly-goals': {
        'task': 'jb_goal_app.tasks.check_goal_task',
        'schedule': crontab(month_of_year=1, day_of_month=1, hour=0, minute=0),  # Run yearly on Jan 1st at midnight
        'args': ('yearly',),
    },
}

```

---

## Set Up and Starting Celery Beat 
- Make sure your **RabbitMQ** instance is running on Docker Desktop (**Default Cred**)
   - Check if your instance is running [here](http://localhost:15672)
   - Username: guest
   - Password: guest
- Your other **stacks**
   - Celery 
      - `celery -A jb_goal worker -l info --pool=solo`
   - Flower 
      - `celery flower -A jb_goal --port=5555`
      - Check if your instance is running [here](http://localhost:5555/)
   - Django Server 
      - `py manage.py runserver`

Let's setup **Celery Beat**

Add `django_celery_beat` to **INSTALL_APP** in `settings.py`

```python
INSTALLED_APPS = [
    # Default apps
    ....
    # My apps
    'jb_goal_app',
    'django_celery_beat'
]
```

**Celery Beat** adds extra tables so we must **update our database**

`py manage.py migrate`

Running **Celery Beat** (Remember to change jb_goal based on your Project Name)

`celery -A jb_goal beat -l info`

---

## Using this example project?

If you're using this project make sure you make your **Own VENV**
`python -m venv venv`

Activate your venv 
`venv/scripts/activate` 

Install my `requirements.txt`
`pip install -r requirements.txt`

There's a known problem with flower and you could fix it by accessing your `venv`

Find Asyncio in your Venv folder
`venv/lib/tornado/platform/asyncio.py`

add this code:

```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```