from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

#1,加载环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

#2,创建celery对象
app = Celery('meiduo_mall')

#3,加载配置
app.config_from_object('celery_tasks.config', namespace='CELERY')

#4,注册任务
app.autodiscover_tasks(["celery_tasks.test.tasks","celery_tasks.sms.tasks"])

#启动celery
# celery -A celery_tasks.main worker -l info

# @app.task(bind=True)
# def add(self, x, y):
#     try:
#         raise Exception("重试")
#         return x + y
#     except Exception as exc:
#         print("重试")
#         raise self.retry(countdown=5, max_retries=3, exc=exc)
