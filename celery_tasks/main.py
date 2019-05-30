from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

#1,设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

#2,创建celery对象
app = Celery('meiduo_mall')

#3,加载配置文件
app.config_from_object('celery_tasks.config', namespace='CELERY')

#4,注册任务,里面放的是模块中的任务文件
app.autodiscover_tasks(["celery_tasks.test.tasks","celery_tasks.sms.tasks","celery_tasks.email.tasks"])

#启动celery任务
# celery -A celery_tasks.main worker -l info

#装饰任务
# @app.task(bind=True,name="xixi")
# def debug_task(self,count):
#     import time
#     for i in range(0,count):
#         time.sleep(1)
#         print("i = %s"%i)