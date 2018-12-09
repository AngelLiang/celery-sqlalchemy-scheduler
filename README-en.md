# celery-sqlalchemy-scheduler

A scheduler based sqlalchemy for celery.

# Installation

Install from source by cloning this repository:

```
$ git clone git@github.com:AngelLiang/celery-sqlalchemy-scheduler.git
$ cd celery-sqlalchemy-scheduler
$ python setup.py install
```

# Usage

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
