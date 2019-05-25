# celery-sqlalchemy-scheduler

一个基于 sqlalchemy 的 scheduler，作为 celery 定时任务的辅助工具。

## 快速开始

[中文文档](/README-zh.md) [English](/README.md)

### 依赖

- Python 3
- celery >= 4.2.0
- sqlalchemy

首先必须安装 `celery` 和 `sqlalchemy`, 并且`celery`应该大于等于 4.2.0 版本。

```
$ pip install celery sqlalchemy
```

### 安装

通过 PyPi 安装：

```
$ pip install celery-sqlalchemy-scheduler
```

通过 github 仓库进行安装：

```
$ git clone git@github.com:AngelLiang/celery-sqlalchemy-scheduler.git
$ cd celery-sqlalchemy-scheduler
$ python setup.py install
```

## 使用示例

安装`celery_sqlalchemy_scheduler`之后，你可以查看`examples`目录下的代码：

1. 启动 celery worker：

   ```
   $ celery worker -A tasks -l info
   ```

2. 使用`DatabaseScheduler`作为 scheduler 启动 celery beat：

   ```
   $ celery beat -A tasks -S celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler -l info
   ```

## 使用说明

beat 启动之后，默认会在当前目录下生成名称为`schedule.db`的 sqlite 数据库。Windows 下可以使用 SQLiteStudio.exe 工具打开查看里面的数据。

![sqlite](screenshot/sqlite.png)

### 数据库同步 scheduler 到 beat

当需要更新 scheduler，只需要修改`schedule.db`相关数据即可。修改好数据库的 scheduler 后，`celery_sqlalchemy_scheduler`并不会马上同步数据库的数据到 beat，我们最后还需要修改`celery_periodic_task_changed`表的第一条数据，只需要把`last_update`字段更新到最新的时间即可。当 beat 在下一个“心跳”之后，就会同步数据库的数据到 beat。

## 配置数据库

在配置 Celery 的时候，可以设置 sqlalchemy 数据库的路径，示例如下：

```Python
from celery import Celery

celery = Celery('tasks')

beat_dburi = 'sqlite:///schedule.db'

celery.conf.update(
    {'beat_dburi': beat_dburi}
)
```

当然，你可以改为使用 MySQL 或 PostgreSQL：

```Python
# MySQL: `pip install mysql-connector`
beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1:3306/celery-schedule'

# PostgreSQL: `pip install psycopg2`
beat_dburi = 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/celery-schedule'
```

## 完整示例代码

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
}

beat_scheduler = 'celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler'

beat_sync_every = 0

# The maximum number of seconds beat can sleep between checking the schedule.
# default: 0
beat_max_loop_interval = 10

# 非celery和beat的配置，配置beat_dburi数据库路径
beat_dburi = 'sqlite:///schedule.db'
# OR
# beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1/celery-schedule'

# 配置时区
timezone = 'Asia/Shanghai'

# 默认每个worker跑完10个任务后，自我销毁程序重建来释放内存
# 防止内存泄漏
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

## 参考

本工具主要参考了以下资料和源码：

- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
