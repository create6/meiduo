from celery_tasks.main import app
#装饰任务
@app.task(bind=True)
def debug_task(self,num):
    import time

    for i in range(0,num):
        time.sleep(1)
        print("i = %s"%i)
