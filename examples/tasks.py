# coding=utf-8
"""
Run Worker:

    $ celery worker -A examples.tasks:celery -l info

Run Beat:

    $ celery beat -A examples.tasks.celery -S examples.tasks:DatabaseScheduler -l info

"""
from datetime import timedelta
from celery import Celery

from celery_sqlalchemy_scheduler.schedulers import DatabaseScheduler  # noqa

backend = 'rpc://'
broker_url = 'amqp://guest:guest@localhost:5672//'

# 如果数据库修改了下面的schedule，beat重启后数据库会被下面的配置覆盖
beat_schedule = {
    'echo-every-3-seconds': {
        'task': 'examples.tasks.echo',
        'schedule': timedelta(seconds=3),
        'args': ('hello', )
    },
    # 'add-every-7-seconds': {
    #     'task': 'examples.tasks.add',
    #     'schedule': timedelta(seconds=7),
    #     'args': (1, 2)
    # },
}
beat_scheduler = 'celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler'
beat_sync_every = 0
# The maximum number of seconds beat can sleep between checking the schedule.
# default: 0
beat_max_loop_interval = 10
# 自定义配置
beat_dburi = 'sqlite:///schedule.db'

# 配置时区
timezone = 'Asia/Shanghai'

celery = Celery('tasks',
                backend=backend,
                broker=broker_url)

config = dict(
    beat_schedule=beat_schedule,
    beat_scheduler=beat_scheduler,
    beat_max_loop_interval=beat_max_loop_interval,
    beat_dburi=beat_dburi,

    timezone=timezone
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
