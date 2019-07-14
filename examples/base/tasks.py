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
import time
import platform
from datetime import timedelta

from celery import Celery
from celery import schedules

from celery_sqlalchemy_scheduler.schedulers import DatabaseScheduler  # noqa

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=True)

ECHO_EVERY_MINUTE = os.getenv('ECHO_EVERY_MINUTE', '0')
ECHO_EVERY_HOUR = os.getenv('ECHO_EVERY_HOUR', '8')

if platform.system() == 'Windows':
    # Celery在Windows环境下运行需要设置这个变量，否则调用任务会报错
    os.environ['FORKED_BY_MULTIPROCESSING'] = '1'

backend = 'rpc://'
broker_url = 'amqp://guest:guest@localhost:5672//'


# 如果数据库修改了下面的schedule，beat重启后数据库会被下面的配置覆盖
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
    'echo-every-hours': {
        'task': 'tasks.echo',
        'schedule': schedules.crontab(ECHO_EVERY_MINUTE, '*', '*'),
        'args': ('echo-every-hours',)
    },
    'echo-every-days': {
        'task': 'tasks.echo',
        'schedule': schedules.crontab(ECHO_EVERY_MINUTE, ECHO_EVERY_HOUR, '*'),
        'args': ('echo-every-days',)
    },
}

beat_scheduler = 'celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler'

beat_sync_every = 0

# The maximum number of seconds beat can sleep between checking the schedule.
# default: 0
beat_max_loop_interval = 10

# 非celery和beat的配置，配置beat_dburi数据库路径
beat_dburi = 'sqlite:///schedule.db'
# beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1/celery-schedule'

# 配置时区
timezone = 'Asia/Shanghai'

# 默认每个worker跑完10个任务后，自我销毁程序重建来释放内存
# 防止内存泄漏
worker_max_tasks_per_child = 10

celery = Celery('tasks',
                backend=backend,
                broker=broker_url)

config = {
    'beat_schedule': beat_schedule,
    # 'beat_scheduler': beat_scheduler,
    'beat_max_loop_interval': beat_max_loop_interval,
    'beat_dburi': beat_dburi,

    'timezone': timezone,
    'worker_max_tasks_per_child': worker_max_tasks_per_child
}

celery.conf.update(config)


@celery.task
def add(x, y):
    return x + y


@celery.task
def echo(data):
    print(data)


if __name__ == "__main__":
    celery.start()
