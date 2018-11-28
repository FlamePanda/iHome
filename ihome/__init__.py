# app初始化

from flask import Flask
from ihome.config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import logging
import logging.handlers
import redis
import pymysql

# 设置数据库安装模式
pymysql.install_as_MySQLdb()

# 数据库
db = SQLAlchemy()

# 得到Redis连接
get_redis_connect = None

# 设置日志
logging.basicConfig(level=logging.DEBUG) # flask开启debug模式会强制设置为logging.DEBUG,无法更改
file_log_handler = logging.handlers.RotatingFileHandler('ihome/logs/log',maxBytes=1024*1024*100,backupCount=10) # 设置日志处理器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s') # 设置输出格式
file_log_handler.setFormatter(formatter) # 绑定格式
logging.getLogger().addHandler(file_log_handler) # 添加处理

# 
def create_app(config_name):
	'''app创建工厂方法
	@params:config_name: str 配置名称 ('develop','product')
	@return:app APP应用
	'''
	# 校验参数
	if config_name not in ['develop','product']:
		# 抛出异常
		raise Exception('%s,配置名称错误！不是[develop,product]的一个'%(config_name))
	# 创建APP
	app = Flask(__name__)
	
	# 配置app
	config_class = config_map.get(config_name)
	app.config.from_object(config_class)
	
	# 绑定数据库
	db.init_app(app)

	# 注册session为Redis缓存
	Session(app)
	
	# 得到Redis连接
	global get_redis_connect
	get_redis_connect = redis.Redis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT,db=config_class.REDIS_DB)
	
	# csrf防护
	CSRFProtect(app)
	
	# 注册蓝图
	from ihome import api_0_1
	app.register_blueprint(api_0_1.api,url_prefix='/api/v1.0')
 
	# 返回app
	return app
