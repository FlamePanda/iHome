from . import api
from ihome.utils.captcha import captcha
from ihome.utils import response_code
from ihome import get_redis_connect,db
from flask import current_app,jsonify,make_response,request
from ihome import constants
from ihome.libs.sms.SendTemplateSMS import SMS
import re
from ihome.models import User
import random

# 使用restful风格

# 请求URL  /api/v1.0/imageCode/<code>
# 请求资源：图片验证码 
# 返回信息：正常：图片，异常：json
@api.route('/imageCode/<code>')
def get_picture_captcha(code):
	# 接收参数
	# 已接收
	# 校验参数
	# 已校验
	# 业务处理
	name,image_code,image_data = captcha.captcha.generate_captcha() # 生成验证码
	try:
		# 存到Redis数据库中
		get_redis_connect.setex('image_code_%s'%(code),constants.CAPTCHA_EXPIRE,image_code)
	except Exception as ex:
		# 记录到日志中
		current_app.logger.error(ex)
		return jsonify(errorno=response_code.RET.DBERR,errormsg="save captcha's code failed!")
	# 返回应答
	response = make_response(image_data)
	response.headers['Content-Type'] = 'image/jpeg'
	return response


# rul:/smsCode/<code>?phone_number=?&picture_code=?
# 请求资源：短信验证码
# 返回类型：正常：json，异常：json
@api.route('/smsCode/<code>')
def get_sms_captcha(code):
	''' 接收参数 '''
	# 接收参数
	phone_number = request.args.get('phone_number')
	picture_code = request.args.get('picture_code')

	''' 校验参数 '''
	# 校验参数
	if not all([phone_number,picture_code]):
		# 参数不完整
		return jsonify(errorno=response_code.RET.PARAMERR,errormsg='missing arguments')

	if not re.match(r'^1(3[0-9]|5[189]|8[6789])[0-9]{8}$',phone_number):
		# 手机号无效
		return jsonify(errorno=response_code.RET.DATAERR,errormsg='invalid  phone number!')

	# 清除picture code
	try:
		get_redis_connect.delete(code)
	except Exception as ex:
		current_app.logger.error(ex)

	# 获取当前手机是否已发送验证码
	try:
		mobile = get_redis_connect.get('mobile_%s'%(phone_number))
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	if mobile is not None:
		# 短信验证码请求频繁
		return jsonify(errorno=response_code.RET.REQERR,errormsg='Frequent operation!')
	
	# 设置手机号获取短信验证码的间隔
	try:
		get_redis_connect.setex('mobile_%s'%(phone_number),constants.SMS_CAPTCHA_SEND_TIME,0)
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)

	# 验证手机号是否已注册
	try:
		user = User.query.filter_by(mobile=phone_number).first()
		if user is not None:
			# 手机号已经注册
			return jsonify(errorno=response_code.RET.DATAEXIST,errormsg='phone number had existed')
	except Exception as ex:
		# Mysql数据库异常
		current_app.logger.error(ex)

	''' 业务处理 '''
	# 取出真实值
	try:
		really_code = get_redis_connect.get('image_code_%s'%code)
	except Exception as ex:
		# Redis数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=response_code.RET.SERVERERR,errormsg='redis server error!')
	# 判断really_code是否存在
	if not really_code:
		return jsonify(errorno=response_code.RET.DATAERR,errormsg='Verification code has expired!')
	# 比较真实值
	if really_code.decode('utf-8').upper() != picture_code.upper():
		# 图片验证码不一致
		return jsonify(errorno=response_code.RET.DATAERR,errormsg='captcha error!')
	
	# 生成随机的6位数字
	num = '%06d'%random.randint(0,999999)

	# 保存随机数num
	try:
		get_redis_connect.setex('%s_num'%(phone_number),constants.SMS_CAPTCHA_EXPIRE,num)
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=response_code.RET.SERVERERR,errormsg='redis error!')
	
	# 发送验证码短信
	reslut = None
	try:
		sms = SMS()
		data = [num,str(int(constants.SMS_CAPTCHA_EXPIRE/60))]
		#reslut = sms.sendTemplateSMS(to=phone_number,datas=data,tempId=1)
		reslut = True
		print('num:',num)
	except Exception as ex:
		# 第三方系统错误
		current_app.logger.error(ex)
		return jsonify(errorno=response_code.RET.THIRDERR,errormsg='Third-party system error!')
	''' 返回应答 '''
	if reslut:
		# 发送成功
		return jsonify(errorno=response_code.RET.OK,errormsg='successful send!')
	else:
		# 发送失败
		return jsonify(errorno=response_code.RET.THIRDERR,errormsg='Third-party system error!')

