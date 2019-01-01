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
$ pip install celery
$ pip install sqlalchemy
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

当然，你可以改为使用 MySQL 数据库：

```Python
# 需要安装mysqlconnector：`pip install mysql-connector`
beat_dburi = 'mysql+mysqlconnector://root:root@127.0.0.1/celery-schedule'
```

## 参考

本工具主要参考了以下资料和源码：

- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
