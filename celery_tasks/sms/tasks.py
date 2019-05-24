from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP

#发送短信
#bind: 表示第一个传递的对象是celery
#name: 任务的名字
#retry_backoff: 重试时间间隔
@app.task(bind=True,name="send_sms_code")
def send_sms_code(self,mobile,sms_code,time):

    #1,发送短信
    try:
        ccp = CCP()
        result =  ccp.send_template_sms(mobile, [sms_code, time], 1)
    except Exception as e:
        raise self.retry(exc=e,countdown=5,max_retries=3)

    #2,判断是否发送成功
    if result != 0:
        print("重试..%s"%result)
        #exec: 异常信息,  countdown:发送短信间隔时间, max_retries: 重试次数
        raise self.retry(exc=Exception("发送短信失败啦!!"), countdown=5, max_retries=3)

    return result