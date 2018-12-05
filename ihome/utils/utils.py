

# 自定义装换器
from werkzeug.routing import BaseConverter

class ReConverter(BaseConverter):
	'''自定义通用装换器'''
	
	def __init__(self,url_map,regex):
		# 调用父类的装换器初始化方法
		super().__init__(url_map)
		# 覆盖父类的regex属性
		self.regex = regex

	def to_python(self,value):
		return value

	def to_url(self,value):
		return value
	


# 验证用户是否登陆的装饰器
from flask import session,g,jsonify
import functools 
from ihome.utils.response_code import RET

def loginrequired(view_fuc):
	'''登陆视图装饰器'''
	
	@functools.wraps(view_fuc)
	def wrapper(*args,**kwargs):
		# 验证用户是否登陆
		user_name = session.get('userName')
		user_id = session.get('userID')
		user_mobile = session.get('phone_number')
		g.user_name = user_name
		g.user_id = user_id
		g.user_mobile = user_mobile
		if all([user_name,user_id,user_mobile]):
			# 用户已登录
			return view_fuc(*args,**kwargs)
		else:
			# 返回json
			return jsonify(errorno=RET.SESSIONERR,errormsg='user not login')
	return wrapper
