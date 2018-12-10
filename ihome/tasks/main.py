from celery import Celery
from ihome.tasks import celeryconfig

celery_app = Celery('ihome')
celery_app.config_from_object(celeryconfig)


# 获取任务
celery_app.autodiscover_tasks(["ihome.tasks.sms"],"tasks")
#from ihome.tasks.sms import tasks


'''
celery 异步任务处理           生产者 中间人 消费者
发布任务命令：函数名.delay(*args,**kwargs)
启动工人命令：celery -A ihome.tasks.main worker -l info #(打印信息)
'''
