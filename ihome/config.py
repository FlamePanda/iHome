# 应用配置类
import redis

class Config(object):
	'''项目配置基础类'''
	
	# 秘钥
	SECRET_KEY = "chenkongd*g^dsf%q$iengsf8(faf3" 
	
	# 数据库配置
	SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost/ihome"
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	
	# 设置Redis的IP，端口号和要使用的数据库
	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = 6379
	REDIS_DB = 0
	
	# 使用Redis配置session缓存
	SESSION_TYPE = "redis"
	SESSION_REDIS = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB) # redis实例
	SESSION_USE_SIGNER = True # 加密session数据
	PERMANENT_SESSION_LIFETIME = 3600*24 # session的有效期一天
	
	# 

class DevelopmentConfig(Config):
	'''开发环境配置类'''
	# 开启调试
	DEBUG = True

class ProductionConfig(Config):
	'''开发环境配置类'''
	pass

# config映射
config_map = {
	'develop':DevelopmentConfig,
	'product':ProductionConfig
}
