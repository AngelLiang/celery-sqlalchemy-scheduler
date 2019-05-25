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

### `examples/base/tasks.py`

```python
# coding=utf-8
"""
Ready::

    $ pipenv install
    $ pipenv shell
    $ python setup.py install

Run Worker::

    $ cd examples/base
    $ celery worker -A tasks:celery -l info

Run Beat::

    $ cd examples/base
    $ celery beat -A tasks:celery -S tasks:DatabaseScheduler -l info

"""
import os
import platform
from datetime import timedelta
from celery import Celery
from celery import schedules

from celery_sqlalchemy_scheduler.schedulers import DatabaseScheduler  # noqa

if platform.system() == 'Windows':
    # If you use celery>=4.2.0 in Windows, you should set this variable
    os.environ['FORKED_BY_MULTIPROCESSING'] = '1'

backend = 'rpc://'
broker_url = 'amqp://guest:guest@localhost:5672//'

# If you changed the data of schedule as below in database,
# the data in database will reset when you restart beat.
beat_schedule = {
    'echo-every-3-seconds': {
        'task': 'tasks.echo',
        'schedule': timedelta(seconds=3),
        'args': ('hello', )
    },
    'add-every-minutes': {
        'task': 'tasks.add',
        'schedule': schedules.crontab('*', '*', '*'),
        'args': (1, 2)
    },
}

beat_scheduler = 'celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler'

beat_sync_every = 0

# The maximum number of seconds beat can sleep between checking the schedule.
# default: 0
beat_max_loop_interval = 10

beat_dburi = 'sqlite:///schedule.db'
# OR
# beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1/celery-schedule'

timezone = 'Asia/Shanghai'

# prevent memory leaks
worker_max_tasks_per_child = 10

celery = Celery('tasks',
                backend=backend,
                broker=broker_url)

config = dict(
    beat_schedule=beat_schedule,
    beat_scheduler=beat_scheduler,
    beat_max_loop_interval=beat_max_loop_interval,
    beat_dburi=beat_dburi,

    timezone=timezone,
    worker_max_tasks_per_child=worker_max_tasks_per_child
)

celery.conf.update(config)


@celery.task
def add(x, y):
    return x + y


@celery.task
def echo(data):
    print(data)


if __name__ == "__main__":
    celery.start()

```

## Acknowledgments

- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
