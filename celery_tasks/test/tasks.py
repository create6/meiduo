from celery_tasks.main import app


@app.task(bind=True,name="xixi")
def debug_task(self,count):
    import time
    for i in range(0,count):
        time.sleep(1)
        print("i = %s"%i)