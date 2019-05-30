from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import app

@app.task(bind=True,name="send_verify_url")
def send_verify_url(self,verify_url,email):
    #1,发送短信
    result = -1
    try:
        result = send_mail(subject='美多商城邮箱激活',
                  message=verify_url,
                  from_email=settings.EMAIL_FROM,
                  recipient_list=[email])
    except Exception as e:
        result = -1

    #2,判断结果
    if result == -1:
        print("重试中....")
        self.retry(countdown=5,max_retries=3,exc=Exception("发送邮件失败啦!!!"))
