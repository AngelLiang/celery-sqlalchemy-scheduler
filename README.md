# celery-sqlalchemy-scheduler

A Scheduler Based Sqlalchemy for Celery.

## Getting Started

[English](/README.md) [中文文档](/README-zh.md)

### Prerequisites

- Python 3
- celery >= 4.2.0
- sqlalchemy

First you must install `celery` and `sqlalchemy`, and `celery` should be >=4.2.0.

```
$ pip install celery
$ pip install sqlalchemy
```

### Installing

Install from PyPi:

```
$ pip install celery-sqlalchemy-scheduler
```

Install from source by cloning this repository:

```
$ git clone git@github.com:AngelLiang/celery-sqlalchemy-scheduler.git
$ cd celery-sqlalchemy-scheduler
$ python setup.py install
```

## Usage

After you have installed `celery_sqlalchemy_scheduler`, you can easily start with following steps:

This is a demo for exmaple, you can check the code in `examples` directory

1. start celery worker

   ```
   $ celery worker -A tasks -l info
   ```

2. start the celery beat with `DatabaseScheduler` as scheduler:

   ```
   $ celery beat -A tasks -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler -l info
   ```

## Description

After the celery beat is started, by default it create a sqlite database(`schedule.db`) in current folder. You can use `SQLiteStudio.exe` to inspect it.

![sqlite](screenshot/sqlite.png)

When you want to update scheduler, you can update the data in `schedule.db`. But `celery_sqlalchemy_scheduler` don't update the scheduler immediately. Then you shoule be change the first column's `last_update` field in the `celery_periodic_task_changed` to now datetime. Finally the celery beat will update scheduler at next wake-up time.

### Database Configuration

You can configure sqlalchemy db uri when you configure the celery, example as:

```Python
from celery import Celery

celery = Celery('tasks')

beat_dburi = 'sqlite:///schedule.db'

celery.conf.update(
    {'beat_dburi': beat_dburi}
)
```

Also, you can use MySQL or PostgreSQL.

```Python
# MySQL: `pip install mysql-connector`
beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1:3306/celery-schedule'

# PostgreSQL: `pip install psycopg2`
beat_dburi = 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/celery-schedule'
```

## Example Code

### Example creating interval-based periodic task

To create a periodic task executing at an interval you must first
create the interval object:

```python
>>> from celery_sqlalchemy_scheduler.models import PeriodicTask, IntervalSchedule
>>> from celery_sqlalchemy_scheduler.session import SessionManager
>>> from celeryconfig import beat_dburi
>>> session_manager = SessionManager()
>>> engine, Session = SessionManager.create_session(beat_dburi)
>>> session = Session()

# executes every 10 seconds.
>>> schedule = session.query(IntervalSchedule).filter_by(every=10, period=IntervalSchedule.SECONDS).first()
>>> if not schedule:
...     schedule = IntervalSchedule(every=10, period=IntervalSchedule.SECONDS)
...     session.add(schedule)
...     session.commit()
```

That's all the fields you need: a period type and the frequency.

You can choose between a specific set of periods:


-   `IntervalSchedule.DAYS`
-   `IntervalSchedule.HOURS`
-   `IntervalSchedule.MINUTES`
-   `IntervalSchedule.SECONDS`
-   `IntervalSchedule.MICROSECONDS`

*note*:

    If you have multiple periodic tasks executing every 10 seconds,
    then they should all point to the same schedule object.

Now that we have defined the schedule object, we can create the periodic task
entry:

```python
    >>> task = PeriodicTask(
    ...     interval=schedule,                  # we created this above.
    ...     name='Importing contacts',          # simply describes this periodic task.
    ...     task='proj.tasks.import_contacts',  # name of task.
    ... )
    >>> session.add(task)
    >>> session.commit()
```

Note that this is a very basic example, you can also specify the
arguments and keyword arguments used to execute the task, the `queue` to
send it to[\*], and set an expiry time.

Here\'s an example specifying the arguments, note how JSON serialization
is required:

```python
    >>> import json
    >>> from datetime import datetime, timedelta

    >>> periodic_task = PeriodicTask(
    ...     interval=schedule,                  # we created this above.
    ...     name='Importing contacts',          # simply describes this periodic task.
    ...     task='proj.tasks.import_contacts',  # name of task.
    ...     args=json.dumps(['arg1', 'arg2']),
    ...     kwargs=json.dumps({
    ...        'be_careful': True,
    ...     }),
    ...     expires=datetime.utcnow() + timedelta(seconds=30)
    ... )
    ... session.add(periodic_task)
    ... session.commit()
```

### Example creating crontab-based periodic task

A crontab schedule has the fields: `minute`, `hour`, `day_of_week`,
`day_of_month` and `month_of_year`, so if you want the equivalent of a
`30 * * * *` (execute every 30 minutes) crontab entry you specify:

    >>> from celery_sqlalchemy_scheduler.models import PeriodicTask, CrontabSchedule
    >>> import pytz
    >>> schedule = CrontabSchedule(
    ...     minute='30',
    ...     hour='*',
    ...     day_of_week='*',
    ...     day_of_month='*',
    ...     month_of_year='*',
    ...     timezone=pytz.timezone('Canada/Pacific')
    ... )

The crontab schedule is linked to a specific timezone using the
'timezone' input parameter.

Then to create a periodic task using this schedule, use the same
approach as the interval-based periodic task earlier in this document,
but instead of `interval=schedule`, specify `crontab=schedule`:

    >>> periodic_task = PeriodicTask(
    ...     crontab=schedule,
    ...     name='Importing contacts',
    ...     task='proj.tasks.import_contacts',
    ... )
    ... session.add(periodic_task)
    ... session.commit()

### Temporarily disable a periodic task

You can use the `enabled` flag to temporarily disable a periodic task:

    >>> periodic_task.enabled = False
    >>> periodic_task.save()

### Example running periodic tasks

The periodic tasks still need 'workers' to execute them. So make sure
the default **Celery** package is installed. (If not installed, please
follow the installation instructions here:
<https://github.com/celery/celery>)

Both the worker and beat services need to be running at the same time.

1.  Start a Celery worker service (specify your project name):

        $ celery -A [project-name] worker --loglevel=info

2.  As a separate process, start the beat service (specify the 
    scheduler):

        $ celery -A [project-name] beat -l info --scheduler celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler



## Acknowledgments

- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
