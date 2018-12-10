from ihome.libs.sms.SendTemplateSMS import SMS
from ihome.tasks.main import celery_app

@celery_app.task
def send_sms_handler(phone_number,data,temp_id):
	'''发送消息函数'''
	sms = SMS()
	return sms.sendTemplateSMS(to=phone_number,datas=data,tempId=temp_id)

