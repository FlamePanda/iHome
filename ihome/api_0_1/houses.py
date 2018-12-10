from . import api
from ihome import get_redis_connect,storage,db
from flask import current_app,jsonify,g,request,session
import json
from ihome.models import Area,Facility,House,HouseImage,User,Order
from ihome.utils.response_code import RET
from ihome.constants import AREAS_INFO_CACHE_EXPIRED
from ihome.utils.utils import loginrequired
from ihome.constants import AVATAR_URL_PREFIXED
from ihome import constants
from datetime import datetime

#URL :/api/v1.0/areas
#请求方式：get
#传递参数：无
#返回参数：json
#使用Redis缓存
@api.route('/areas')
def get_areas():
	'''处理城区视图函数'''
	# 从Redis获取缓存
	try:
		areas_json_str = get_redis_connect.get('areas_info')
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	else:
		if areas_json_str:
			# 若缓存中有数据，直接返回数据
			return areas_json_str,200,{"Content-Type":"application/json"}
		
	#从mysql获取参数
	try:
		areas = Area.query.all()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
	# 遍历areas
	areas_list = [area.to_dict() for area in areas ]
	#print("areas_list",areas_list)
	# 转成json字符串
	areas_json_str = json.dumps({'errorno':RET.OK,'errormsg':'success','areas':areas_list})
	# 保存到Redis中
	try:
		get_redis_connect.setex('areas_info',AREAS_INFO_CACHE_EXPIRED,areas_json_str)
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	# 返回应答
	return areas_json_str,200,{"Content-Type":"application/json"}

#URL :/api/v1.0/facility
#请求方式：get
#传递参数：
#返回参数：json
@api.route('/facility',methods=['GET'])
@loginrequired
def get_facility():
	'''获取设施的视图处理函数'''
	# 获取设施信息
	try:
		facilities = Facility.query.all()
	except Exception as ex:
		# mysql 数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')

	facilities_list = [facility.to_dict() for facility in facilities]
	#print(facilities_list)
	return jsonify(errorno=RET.OK,errormsg='success',data={'facilities':facilities_list})

#URL :/api/v1.0/houses
#请求方式：post
#传递参数：json
#返回参数：json
@api.route('/houses',methods=['POST'])
@loginrequired
def add_house():
	'''添加房子的视图处理函数'''
	##获取参数
	# 用户ID
	user_id = g.user_id
	# 房子的相关信息
	args_dict = request.get_json()
	#print(args_dict)
	if not args_dict:
		# 没有数据
		return jsonify(errorno=RET.NODATA,errormsg="没有json数据！")
	title = args_dict.get('title')
	price = args_dict.get('price')
	area_id = args_dict.get('area_id')
	address = args_dict.get('address')
	room_count = args_dict.get('room_count')
	acreage = args_dict.get('acreage')
	unit = args_dict.get('unit')
	capacity = args_dict.get('capacity')
	beds = args_dict.get('beds')
	deposit = args_dict.get('deposit')
	min_days = args_dict.get('min_days')
	max_days = args_dict.get('max_days')
	facility_list = args_dict.get('facility')# 可以为空
	##校验参数
	# 校验参数是否为空
	if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
		# 参数不完整
		return jsonify(errorno=RET.PARAMERR,errormsg='missing argments!')
	# 校验room_count,capacity,min_days和max_days是否有效
	for v in [room_count,capacity,min_days,max_days]:
		try:
			if int(v) <= -1:
				# 信息有误
				return jsonify(errorno=RET.PARAMERR,errormsg="argments error!")
		except Exception as ex:
			current_app.logger.error(ex)
			# 信息有误
			return jsonify(errorno=RET.PARAMERR,errormsg="argments error!")
				
	# 校验押金和价格
	try:
		price = int(float(price) * 100)
		deposit = int(deposit)
	except Exception as ex:
		# 价格和押金数值非法
		current_app.logger.error(ex)
		return jsonify(errrono=RET.PARAMERR,errormsg='price or deposit illegal!')
	## 业务处理
	# 构造house
	house = House(user_id=user_id,title=title,price=price,area_id=area_id,address=address,room_count=room_count,acreage=acreage,unit=unit,capacity=capacity,beds=beds,deposit=deposit,min_days=min_days,max_days=max_days) 
	# 取出所有的facility
	if facility_list:
		try:
			facilities = Facility.query.filter(Facility.id.in_(facility_list)).all()
			#print('facilities:',facilities)
		except Exception as ex:
			# mysql数据库异常
			current_app.logger.error(ex)
			return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
		if facilities:
			# 设施信息正常
			house.facilities = facilities
	# 保存进数据库
	try:
		db.session.add(house)
		db.session.commit()
	except Exception as ex:
		# 保存失败，mysql数据库异常
		db.session.rollback()
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error')
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg='success',data={'house_id':house.id})


#URL :/api/v1.0/houses/images
#请求方式：post
#传递参数：(form类型)image,house_id
#返回参数：json
@api.route('/houses/images',methods=['POST'])
@loginrequired
def add_house_image():
	'''添加房子图片的视图处理函数'''
	# 获取参数
	house_id = request.form.get('house_id')
	image_data = request.files.get('house_image')
	# 校验参数
	if not all([house_id,image_data]):
		# 缺少参数
		return jsonify(errorno=RET.PARAMERR,errormsg="missing argments!")
	# 校验house是否存在
	try:
		house = House.query.get(house_id)
	except Exception as ex:
		# mysql 数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='house id not current')
	# 业务处理
	# 保存图片
	try:
		file_name = storage.upload_file(image_data.read())
	except Exception as ex:
		# 第三方系统错误
		current_app.logger.error(ex)
		return jsonify(errorno=RET.THIRDERR,errormsg='fastdfs system error!')
	#创建house_image对象
	house_image = HouseImage(house_id=house.id,url=file_name)
	# 设置house中的url
	if not house.index_image_url:
		house.index_image_url = file_name
	#保存进入数据库
	try:
		db.session.add(house_image)
		db.session.add(house)
		db.session.commit()
	except Exception as ex:
		# mysql数据库异常
		db.session.rollback()
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
	# 返回应答
	image_url = AVATAR_URL_PREFIXED + file_name
	return jsonify(errorno=RET.OK,errormsg='success',data={'image_url':image_url})

# URL :/api/v1.0/users/houses
# 请求方式：get
# 传递参数：session
# 返回参数：json
@api.route('/users/houses',methods=['GET'])
@loginrequired
def get_user_houses():
	'''处理用户发布的房子'''
	# 获取用户id
	user_id = g.user_id
	# 检验参数
	try:
		user = User.query.get(user_id)
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg='mysql server error!')
	else:
		if user is None:
			# 用户不存在
			return jsonify(errorno=RET.ROLEERR,errormsg="user not exist!")
	# 业务处理
	houses = []
	if user.houses:
		houses = [ house.to_base_dict() for house in user.houses]
	# 返回应答
	return jsonify(errorno=RET.OK,errormsg="success",data={"houses":houses})

# URL :/api/v1.0/houses/indexImage
# 请求方式：get
# 传递参数：none
# 返回参数：json
@api.route('/houses/indexImage',methods=['GET'])
def get_index_image():
	'''获取首页轮播展示图片'''
	# 使用Redis缓存首页数据
	try:
		index_image_json_data = get_redis_connect.get("index_images")
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	else:
		if index_image_json_data:
			# 直接返回数据
			print("hit redis index images")
			return '{"errorno":"0","errormsg":"success","data":%s}'%index_image_json_data.decode("utf-8"),200,{"Content-Type":"application/json"} 
	# 业务处理
	try:
		houses = House.query.order_by(House.order_count.desc()).limit(constants.INDEX_IMAGES_MAX_COUNT).all()
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg="mysql server error!")
	else:
		if not houses:
			# 空数据
			return jsonify(errorno=RET.OK,errormsg='no images')
	# 保存数据进入Redis
	index_image_data = [house.to_base_dict() for house in houses]
	index_image_json_data = json.dumps(index_image_data)
	try:
		get_redis_connect.setex("index_images",constants.INDEX_IMAGES_EXPIRED,index_image_json_data)
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	# 返回应答
	return '{"errorno":"0","errormsg":"success","data":%s}'%index_image_json_data,200,{"Content-Type":"application/json"}


# URL :/api/v1.0/houses/<int:house_id>
# 请求方式：get
# 传递参数：url
# 返回参数：json
@api.route('/houses/<int:house_id>',methods=['GET'])
def get_house_verbose(house_id):
	'''房屋的详情页面处理'''
	# 获取参数
	user_id = session.get("userID",-1)
	# 尝试重Redis中直接取回数据直接返回
	try:
		house_verbose_json_str = get_redis_connect.get("house_verbose_%s"%house_id)
	except Exception as ex:
		# redis使句酷异常
		current_app.logger.error(ex)
	else:
		if house_verbose_json_str:
			# 直接返回数据
			print('hit redis house verbose !')
			return '{"errorno":"0","errormsg":"success","data":{"user_id":%s,"house":%s}}'%(user_id,house_verbose_json_str.decode("utf-8")),200,{"Content-Type":"application/json"}
	# 校验参数
	# 参数校验
	if not all([house_id]):
		# 数据不存在
		return jsonify(errorno=RET.NODATA,errormsg="not house data")
	# 用户校验
	if user_id != -1:
		try:
			user = User.query.get(user_id)
		except Exception as ex:
			# mysql数据库异常
			current_app.logger.error(ex)
		else:
			if not user:
				# 用户不存在
				return jsonify(errorno=RET.ROLEERR,errormsg="user auth error!")
	# 房屋校验
	try:
		house = House.query.get(house_id)
	except Exception as ex:
		# mysql数据库异常
		current_app.logger.error(ex)
		return jsonify(errorno=RET.DBERR,errormsg="mysql server error!")
	else:
		if not house:
			# 不存在该房子
			return jsonify(errorno=RET.PARAMERR,errormsg="parameters error!")
	# 业务处理
	data = house.to_verbose_dict()
	house_verbose_json_str = json.dumps(data)
	try:
		# 使用Redis缓存数据
		get_redis_connect.setex("house_verbose_%s"%house_id,constants.HOUSE_VERBOSE_EXPIRED,house_verbose_json_str)
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	
	# 返回应答
	return '{"errorno":"0","errorsmg":"success","data":{"user_id":%s,"house":%s}}'%(user_id,house_verbose_json_str),200,{"Content-Type":"application/json"}


# URL :/api/v1.0/houses
# 请求方式：get
# 传递参数：url aid=12 sd=2018-12-12 ed=2018-12-22 s=new p=1
# 返回参数：json
@api.route('/houses',methods=['GET'])
def search_houses():
	'''根据指定的条件搜索房源'''
	# 获取参数
	area_id = request.args.get("aid","")
	start_time = request.args.get("sd","")
	end_time = request.args.get("ed","")
	sort = request.args.get('s',"new")
	page_index = request.args.get("p",1)
	# 校验参数
	# 日期校验
	try:
		if start_time:
			start_time = datetime.strptime(start_time,"%Y-%m-%d")
		if end_time:
			end_time = datetime.strptime(end_time,"%Y-%m-%d")
		if start_time and end_time:
			assert start_time <= end_time
	except Exception as ex:
		# 日期格式错误
		current_app.logger.error(ex)
		return jsonify(errorno=RET.PARAMERR,errormsg="parameters(date) error!")
	# page_index校验
	try:
		page_index = int(page_index) if int(page_index) > 0 else 1
	except Exception as ex:
		# page错误
		current_app.logger.error(ex)
		return jsonify(errorno=RET.PARAMERR,errormsg="parameters(page) error!")
		
	# area_id 校验
	if area_id:
		try:
			area = Area.query.get(area_id)
		except Exception as ex:
			# mysql数据库异常
			current_app.logger.error(ex)
			return jsonify(errorno=RET.DBERR,errormsg="mysql server error!")
		else:
			if not area:
				# 说明area id 错误
				return jsonify(errorno=RET.PARAMERR,errormsg="parameters(area) error!")
	# 尝试从redis中取出数据
	search_houses_redis_key = "search_houses_%s_%s_%s_%s"%(start_time,end_time,area_id,sort)
	try:
		search_houses_json_str = get_redis_connect.hget(search_houses_redis_key,page_index)
	except Exception as ex:
		# redis 数据库异常
		current_app.logger.error(ex)
	else:
		if search_houses_json_str:
			print("hit redis search_houses_json_str")
			# 直接返回
			return '{"errorno":"0","errormsg":"success","data":%s}'%search_houses_json_str.decode("utf-8"),200,{"Content-Type":"application/json"}
	# 业务处理
	# 获取订单中冲突的时间
	orders = None
	if end_time and start_time:
		orders = Order.query.filter(Order.begin_date < end_time,Order.end_date > start_time).all()
	elif end_time:
		orders = Order.query.filter(Order.begin_date < end_time).all()
	elif start_time:
		orders = Order.query.filter(Order.end_date > start_time).all()
	# 添加筛选条件
	filter_list = []
	# 排除冲突的房源
	if orders:
		filter_list.append(House.id.notin_([order.house_id for order in orders]))
	# 地区条件
	if area_id:
		# 查询条件，area
		filter_list.append(House.area_id == area_id)
	# 根据sort排序
	if sort == "booking":
		# 入住最多
		houses_query = House.query.filter(*filter_list).order_by(House.order_count.desc())
	elif sort == "price-inc":
		# 按价格升序
		houses_query = House.query.filter(*filter_list).order_by(House.price.asc())
	elif sort == "price-des":
		# 按价格降序
		houses_query = House.query.filter(*filter_list).order_by(House.price.desc())
	else:
		# 其他默认最新的排序
		houses_query = House.query.filter(*filter_list).order_by(House.create_time.desc())
	# 对插叙结果分页处理
	page_houses = houses_query.paginate(page=page_index,per_page=constants.PER_PAGE_HOUSES_COUNT,error_out=False)
	houses = [house.to_base_dict() for house in page_houses.items]
	# 最大页数
	page_max_index = page_houses.pages
	# 使用redis缓存数据
	search_houses_json_str = json.dumps({"houses":houses,"max_pages":page_max_index})
	try:
		# 使用redis的pipeline一次执行多个命令
		pipeline = get_redis_connect.pipeline()
		pipeline.multi()# 开启多个命令 或者使用 pipeline.set().set().....
		pipeline.hset(search_houses_redis_key,page_index,search_houses_json_str)
		pipeline.expire(search_houses_redis_key,constants.SEARCH_HOUSES_CACHE_EXPIRED)
		pipeline.execute() # 执行多个命令
	except Exception as ex:
		# redis数据库异常
		current_app.logger.error(ex)
	# 返回应答
	return '{"errorno":"0","errormsg":"success","data":%s}'%search_houses_json_str,200,{"Content-Type":"application/json"}
