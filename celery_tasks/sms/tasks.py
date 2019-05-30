from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP

#bind: 会将第一个参数绑定到函数的第一参数
#name: 表示任务的名称
@app.task(bind=True,name="sms_code")
def send_sms_code(self,mobile,sms_code,time):
    # import time
    # time.sleep(10)
    #1,发送短信
    try:
        ccp = CCP()
        result =  ccp.send_template_sms(mobile, [sms_code, time], 1)
    except Exception as e:
        result = -1

    #2,判断结果
    if result == -1:
        print("重试中....")
        self.retry(countdown=5,max_retries=3,exc=Exception("发送短信失败啦!!!"))
