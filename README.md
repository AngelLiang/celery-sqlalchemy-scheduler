
[![code](https://github.com/aruba-uxi/celery-sqlalchemy-scheduler/actions/workflows/lint-test-code.yaml/badge.svg)](https://github.com/aruba-uxi/celery-sqlalchemy-scheduler/actions/workflows/lint-test-code.yaml)

[![Python Version](https://img.shields.io/badge/python-3.10-blue?logo=Python&logoColor=yellow)](https://docs.python.org/3.10/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build: just](https://img.shields.io/badge/%F0%9F%A4%96%20build-just-black?labelColor=white)](https://just.systems/)


# celery sqlalchemy scheduler

A Scheduler Based Sqlalchemy for Celery.

## Table Of Contents

- [Setup](#setup)
- [Development](#development)
- [Examples](#example-code-1)
- [Version Control](#version-control)
- [Deployment](#deployment)
- [Workflows](#workflows)

## Setup

This project is setup to use [editorconfig](https://editorconfig.org/). Most editors work but some require a plugin like [VSCode](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)

It's advisable to create a virtual environment for this project to keep packages separate.
> **__NOTE__:** Using pyenv, you can run `pyenv virtualenv 3.10.<latest> celery-sqlalchemy-scheduler`

After creating a virtual environment, install the required dependencies.

```sh
just setup-dev
```

### Database Configuration

You can configure sqlalchemy db uri when you configure the celery, for example as:

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


## Development

After you have installed `celery_sqlalchemy_scheduler`, you can easily start with following steps:

This is a demo - you can check the code in the `examples` directory.

1. start celery worker

   ```
   $ celery worker -A tasks -l info
   ```

2. start the celery beat with `DatabaseScheduler` as scheduler:

   ```
   $ celery beat -A tasks -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler -l info
   ```

### Tip
After the celery beat is started, by default it creates a sqlite database(`schedule.db`) in the current folder. You can use `SQLiteStudio.exe` to inspect it.

![sqlite](screenshot/sqlite.png)

When you want to update scheduler, you can update the data in `schedule.db`. But `celery_sqlalchemy_scheduler` won't update the scheduler immediately. Then you should change the first column's `last_update` field in the `celery_periodic_task_changed` to now datetime. Finally the celery beat will update scheduler at the next wake-up time.

## Example Code 1

View `examples/base/tasks.py` for details.

How to quickstart: https://github.com/AngelLiang/celery-sqlalchemy-scheduler/issues/15#issuecomment-625624088

Run Worker in console 1

    $ pipenv shell
    $ cd examples/base

    # Celery < 5.0
    $ celery worker -A tasks:celery -l info

    # Celery >= 5.0
    $ celery -A tasks:celery worker -l info

Run Beat in console 2

    $ pipenv shell
    $ cd examples/base

    # Celery < 5.0
    $ celery beat -A tasks:celery -S tasks:DatabaseScheduler -l info

    # Celery >= 5.0
    $ celery -A tasks:celery beat -S tasks:DatabaseScheduler -l info

## Example Code 2

### Example creating interval-based periodic task

To create a periodic task executing at an interval you must first
create the interval object:

```python
>>> from celery_sqlalchemy_scheduler.models import PeriodicTask, IntervalSchedule
>>> from celery_sqlalchemy_scheduler.session import SessionManager
>>> from celeryconfig import beat_dburi
>>> session_manager = SessionManager()
>>> engine, Session = session_manager.create_session(beat_dburi)
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

- `IntervalSchedule.DAYS`
- `IntervalSchedule.HOURS`
- `IntervalSchedule.MINUTES`
- `IntervalSchedule.SECONDS`
- `IntervalSchedule.MICROSECONDS`

_note_:

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

Here's an example specifying the arguments, note how JSON serialization
is required:

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

### Example creating crontab-based periodic task

A crontab schedule has the fields: `minute`, `hour`, `day_of_week`,
`day_of_month` and `month_of_year`, so if you want the equivalent of a
`30 * * * *` (execute every 30 minutes) crontab entry, you specify:

    >>> from celery_sqlalchemy_scheduler.models import PeriodicTask, CrontabSchedule
    >>> schedule = CrontabSchedule(
    ...     minute='30',
    ...     hour='*',
    ...     day_of_week='*',
    ...     day_of_month='*',
    ...     month_of_year='*',
    ...     timezone='UTC',
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
    >>> session.add(periodic_task)
    >>> session.commit()

> Note: If you want to delete `PeriodicTask`, don't use `.delete()` method on a query
> such as `db.session.query(PeriodicTask).filter(PeriodicTask.id == task_id).delete()`.
> Because it doesn't trigger the `after_delete` event listener and results in Error.
> The correct deletion method is using session to delete `PeriodicTask` object.

    >>> db.session.delete(db.session.query(PeriodicTask).get(task_id))
    >>> db.session.commit()

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


## Version Control

This repo follows the [SemVer 2](https://semver.org/) version format.

Given a version number `MAJOR.MINOR.PATCH`, increment the:

- `MAJOR` version when you make incompatible API changes,
- `MINOR` version when you add functionality in a backwards compatible manner, and
- `PATCH` version when you make backwards compatible bug fixes.

## Workflows

The repository has a number of github workflows defined in the the `.github/workflows` folder.

### Lint Charts

- Tests helm charts for linting and changes

### Lint & Test Code

- Tests the code for linting issues
- Tests the requirements file for any changes

### Release

- Pushes the client to internal gemfury account



## Acknowledgments

- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
- [celery-sqlalchemy-scheduler](https://github.com/AngelLiang/celery-sqlalchemy-scheduler)