from flask import current_app,g,jsonify,request,session
from ihome.utils.utils import loginrequired
from . import api
from ihome.utils.response_code import RET
from ihome import storage,db
from ihome.constants import AVATAR_URL_PREFIXED
from ihome.models import User
import re

# URL: /api/v1.0/users/avatar
# 请求方式：post
# 功能：上传用户头像
# 接收参数：用户ID，头像的二进制数据
# 返回结果：正常 json，异常，json
@api.route('/users/avatar',methods=['POST',])
@loginrequired
def upload_avatar():
	'''处理用户上传头像的视图类'''
	# 接收数据
	user_id = g.user_id
	file_data = request.files.get('avatar')
	# 校验数据
	if not file_data:
		# 没有图片数据
		return jsonify(errorno=RET.NODATA,errormsg='not avatar data!')
	# 业务处理
	# 获取用户
	try:
		user = User.query.filter_by(id=user_id).first()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
	else:
		if not user:
			# 用户不存在
			return jsonify(errorno=RET.USERERR,errormsg='user not exist!')
	
	# 保存图片到第三方系统
	try:
		file_name = storage.upload_file(file_data.read())
	except Exception as ex:
		# 文件上传失败
		current_app.logger.error(ex)
		return jsonify(errorno=RET.THIRDERR,errormsg='fastdfs system error!')
	else:
		if not file_name:
			# 文件上传失败
			return jsonify(errorno=RET.THIRDERR,errormsg='image upload failed!')
	# 保存图片的filename
	old_avatar_url = user.avatar_url
	if old_avatar_url:
		# 删除原有的图片
		try:
			storage.delete_file(old_avatar_url)
		except Exception as ex:
			# fastFds系统错误
			current_app.logger.error(ex)
	user.avatar_url = file_name
	try:
		db.session.commit()
	except Exception as ex:
		# 数据库异常
		db.session.rollback()
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')

	# 返回应答
	avatar_url = AVATAR_URL_PREFIXED + file_name
	return jsonify(errorno=RET.OK,errormsg='upload success!',data={'url':avatar_url})



# URL：/api/v1.0/users
# 请求方式：get
# 功能：请求用户信息
# 接收参数 session
# 返回参数,成功：json，异常：json
@api.route('/users',methods=['GET',])
@loginrequired
def users_info():
	'''用户信息处理视图类'''
	# 获取参数
	user_id = g.user_id
	# 校验参数
	# loginrequired装饰器已校验
	# 业务处理
	try:
		user = User.query.filter_by(id=user_id).first()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
	avatar_url = (AVATAR_URL_PREFIXED + user.avatar_url) if user.avatar_url else ""
	user_name = user.name
	user_mobile = user.mobile
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg='get user info success!',data={"user_mobile":user_mobile,"user_name":user_name,"url":avatar_url})


# URL：/api/v1.0/users/name
# 请求方式：put
# 功能：请求用户信息
# 接收参数 session和json
# 返回参数,成功：json，异常：json
@api.route('/users/name',methods=['PUT',])
@loginrequired
def update_username():
	'''修改用户名字的视图处理函数'''
	# 接收参数
	user_id = g.user_id
	old_user_name = g.user_name
	args_dict = request.get_json()
	new_user_name = args_dict.get('name')
	# 校验参数
	# id loginrequired已校验
	if not new_user_name:
		# 说明缺少参数
		return jsonify(errorno=RET.NODATA,errormsg='missing argments!')
	
	if old_user_name == new_user_name:
		# 说明用户没有修改名字
		return jsonify(errorno=RET.PARAMERR,errormsg="name same to old name!")
	# 业务处理
	try:
		user = User.query.filter_by(id=user_id).update({"name":new_user_name.strip()})
		db.session.commit()
	except Exception as ex:
		# mysql 数据库异常
		db.session.rollback()
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg="the name had existed!")
	session['userName'] = new_user_name
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg="update user name success!",data={'name':new_user_name})

# URL：/api/v1.0/users/auth
# 请求方式：get
# 功能：请求用户实名信息
# 接收参数 session
# 返回参数,成功：json，异常：json
@api.route('/users/auth',methods=['GET',])
@loginrequired
def get_user_auth():
	'''处理请求得到用户实名信息视图处理函数'''
	# 接收参数
	user_id = g.user_id
	# 校验参数
	# loginrequired已校验
	# 业务处理
	try:
		user = User.query.filter_by(id=user_id).first()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg="msyql server error!")
	user_auth_name = user.real_name if user.real_name else ""
	user_auth_id_card = user.id_card if user.id_card else ""
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg="user auth success!",data={'name':user_auth_name,'id_card':user_auth_id_card})

# URL：/api/v1.0/users/auth
# 请求方式：post
# 功能：增加和修改用户实名信息
# 接收参数 json和session
# 返回参数,成功：json，异常：json
@api.route('/users/auth',methods=['POST',])
@loginrequired
def user_auth_handler():
	'''处理请求用户实名信息修改视图处理函数'''
	# 接收参数
	user_id = g.user_id
	args_dict = request.get_json()
	real_user_auth_name = args_dict.get('real_name')
	user_auth_id_card = args_dict.get('id_card')
	# 校验参数
	if not all([real_user_auth_name,user_auth_id_card]):
		# 参数不完整
		return jsonify(errorno=RET.PARAMERR,errromsg="missing argments！")
	# 接入公安系统进行校验
	# 模拟校验
	if not re.match(r'^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',user_auth_id_card):
		# 身份证号码错误
		return jsonify(errorno=RET.PARAMERR,errormsg="id card error!")
	
	# 业务处理
	try:
		User.query.filter_by(id=user_id,real_name=None,id_card=None).update({'real_name':real_user_auth_name,'id_card':user_auth_id_card})
		db.session.commit()
	except Exception as ex:
		# 数据库异常
		db.session.rollback()
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg="mysql server error!")	
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg="setup  success!",data={'real_name':real_user_auth_name,'id_card':user_auth_id_card})
