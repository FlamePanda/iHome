from . import api
from flask import request,current_app,jsonify,session,g
from ihome.utils.response_code import RET
from ihome.utils.utils import loginrequired
from ihome import get_redis_connect,db
from ihome.models import User
from sqlalchemy.exc import IntegrityError
import re
from werkzeug.security import check_password_hash
from ihome import constants

# URL：/api/v1.0/users
# 请求方式：post
# 功能：用户注册
# 接收参数 json格式，phone_number,sms_code,password,ensure_password
# 返回参数,成功：跳转首页，异常：json
@api.route('/users',methods=['POST',])
def users_register():
	'''用户注册'''
	# 提取参数
	args_dict = request.get_json()
	phone_number = args_dict.get('phone_number')
	sms_code = args_dict.get('sms_code')
	password = args_dict.get('password')
	ensure_password = args_dict.get('ensure_password')

	# 校验参数
	if not all([phone_number,sms_code,password,ensure_password]):
		# 缺少参数，参数不完整
		return jsonify(errorno=RET.NODATA,errormsg='missing arguments!')
	
	if password != ensure_password:
		# 两次密码不一致
		return jsonify(errorno=RET.PARAMERR,errormsg='Two passwords are inconsistent!')
	
	if not re.match(r'^1(3[0-9]|5[189]|8[6789])[0-9]{8}$',phone_number):
		# 手机号格式不正确
		return jsonify(errorno=RET.PARAMERR,errormsg='Phone number format is not correct!')
	
		
	# 业务处理
	really_sms_code = None
	try:
		really_sms_code = get_redis_connect.get('%s_num'%(phone_number))
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='redis server error!')
	else:
		if really_sms_code is None:
			# 短信验证码已过期
			return jsonify(errorno=RET.NODATA,errormsg='SMS verification code has expired!')

	# 删除短信验证码
	try:
		get_redis_connect.delete('%s_num'%(phone_number))
	except Exception as ex:
		# Redis数据库异常
		current_app.logger.error(ex)

	# 校验短信验证码
	if sms_code != really_sms_code.decode('utf-8'):
		# 短信验证码出错
		return jsonify(errorno=RET.DATAERR,errormsg='SMS verification code error!')
	
	# 注册用户
	user = User(name=phone_number,mobile=phone_number)
	user.password = password
	try:
		db.session.add(user)
		db.session.commit()
	except IntegrityError as ex:
		# 手机号已注册
		db.session.rollback() # 回滚
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DATAEXIST,errormsg='the phone number exist')
	except Exception as ex:
		# 数据库异常
		db.session.rollback() # 回滚
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql database insert error!')
	# 保存用户登录状态
	session['userName'] = user.name
	session['userID'] = user.id
	session['phone_number'] = phone_number
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg='register success!')


# URL:/api/v1.0/sessions
# 请求方式：post
# 功能：用户登录
# 接收参数 json格式，phone_number,password
# 返回参数,成功：跳转首页，异常：json
@api.route('/sessions',methods=['POST',])
def users_login():
	'''用户登录视图函数'''
	# 接收参数
	args_dict = request.get_json()
	phone_number = args_dict.get('phone_number')
	password = args_dict.get('password')
	# 校验参数
	if not all([phone_number,password]):
		# 参数不完整
		return jsonify(errorno=RET.NODATA,errormsg="missing arguments!")

	if not re.match(r'^1(3[0-9]|5[189]|8[6789])[0-9]{8}$',phone_number):
		# 手机号格式不对
		return jsonify(errorno=RET.PARAMERR,errormsg='Phone number format is not correct!')

	# 获取手机号的错误次数
	access = 'access_num_%s'% request.remote_addr
	try:
		access_nums = get_redis_connect.get(access)
	except Exception as ex:
		# Redis数据库异常
		current_app.logger.error(ex)
	else:
		if access_nums is not None	and int(access_nums) >= constants.USER_LOGIN_ERROR_NUMS:
			# 若输错的密码次数大于规定的次数，则禁止该IP登录
			return jsonify(errorno=RET.REQERR,errormsg='Please try again in 10 minutes.') 
	
	# 业务处理
	user = None
	try:
		user = User.query.filter_by(mobile=phone_number).first()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql database select error!')		
	# 用户是否存在
	if user is None:
		# 该手机号未注册
		return jsonify(errorno=RET.USERERR,errormsg='the phone number not exist!')
	# 用户密码是否正确
	password_hash = user.password_hash
	# 返回应答
	if check_password_hash(password_hash,password):
		# 用户存在。密码正确
		# 记录用户登录状态
		session['userName'] = user.name
		session['userID'] = user.id
		session['phone_number'] = phone_number
		return jsonify(errorno=RET.OK,errormsg='login success')
	else:
		# 用户密码错误
		# 获取手机号的错误次数
		try:
			get_redis_connect.incr(access)
			get_redis_connect.expire(access,constants.USER_PROHIBIT_LOGIN_TIME)
		except Exception as ex:
			# Redis数据库异常
			current_app.logger.error(ex)
		return jsonify(errorno=RET.PWDERR,errormsg='the password or phone number  error')


# URL:/api/v1.0/session
# 请求方式：delete
# 功能：用户登出
# 接收参数 session
# 返回参数,成功：跳转登录页面，异常：json
@api.route('/session',methods=['DELETE',])
@loginrequired
def users_logout():
	'''用户登出视图函数'''
	# 获取参数
	# 校验参数
	# 业务处理
	# 清除session数据
	session.clear()
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg='logout success!')

# URL:/api/v1.0/session
# 请求方式：get
# 功能：用户是否已登录
# 接收参数 session
# 返回参数,成功：json
@api.route('/session')
def users_status():
	'''用户登出视图函数'''
	# 获取参数
	user_id = session.get('userID')
	user_name = session.get('userName')
	user_mobile = session.get('phone_number')
	# 校验参数
	if not all([user_id,user_name,user_mobile]):
		return jsonify(errorno=RET.PARAMERR,errormsg='missming arguments!')
	# 业务处理
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg='login success!',data=user_name)


