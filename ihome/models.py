from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash
from ihome.constants import AVATAR_URL_PREFIXED,HOUSE_VERBOSE_INFO_MAX_COMMENT

class BaseModel(object):
	"""模型基类，为每个模型补充创建时间与更新时间"""
	
	create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录更新时间
	is_delete = db.Column(db.Boolean,default=False,nullable=False) # 是否删除

class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户暱称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    houses = db.relationship("House", backref="user")  # 用户发布的房屋
    orders = db.relationship("Order", backref="user")  # 用户下的订单

    @property
    def password(self):
        # 此方法不能被调用
        raise AttributeError(' password cannot be called!')

    @password.setter
    def password(self,value):
        # 生成加密字符串
        self.password_hash = generate_password_hash(value)

class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "ih_area_info"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    houses = db.relationship("House", backref="area")  # 区域的房屋
    
    def to_dict(self):
        '''返回对象字典'''
        d = {'id':self.id,'name':self.name}
        return d


# 房屋设施表，建立房屋与设施的多对多关系
house_facility = db.Table(
    "ih_house_facility",
	db.Column("house_id", db.Integer, db.ForeignKey("ih_house_info.id"), primary_key=True),  #房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey("ih_facility_info.id"), primary_key=True)  # 设施编号
)


class House(BaseModel, db.Model):
    """房屋信息"""

    __tablename__ = "ih_house_info"

    id = db.Column(db.Integer, primary_key=True)  # 房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)# 房屋主人的用户编号
    area_id = db.Column(db.Integer, db.ForeignKey("ih_area_info.id"), nullable=False)#归属地的区域编号
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径
    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋的设施
    images = db.relationship("HouseImage")  # 房屋的图片
    orders = db.relationship("Order", backref="house")  # 房屋的订单


    def to_base_dict(self):
        '''房子的基本信息'''
        d = {"order_count":self.order_count,"address":self.address,"room_count":self.room_count,"user_avatar_url":AVATAR_URL_PREFIXED+self.user.avatar_url,"user_id":self.user_id,"house_id":self.id,"title":self.title,"area":self.area.name,"price":self.price//100,"image_url":AVATAR_URL_PREFIXED+self.index_image_url,"ctime":self.create_time.strftime("%Y-%m-%d %H:%M:%S")}
        return d


    def to_verbose_dict(self):
        '''房子的详细信息'''
        d = {"user_name":self.user.name,"user_avatar_url":AVATAR_URL_PREFIXED+self.user.avatar_url,"user_id":self.user_id,"house_id":self.id,"title":self.title,"area":self.area.name,"price":self.price//100,"address":self.address,"room_count":self.room_count,"acreage":self.acreage,"unit":self.unit,"capacity":self.capacity,"beds":self.beds,"deposit":self.deposit,"min_days":self.min_days,"max_days":self.max_days,}
        
        # 获取所有的房屋图片
        d["images_url"] = [AVATAR_URL_PREFIXED+image.url for image in self.images]
	
        # 获取所有的设施名字
        d["facility_name"] = [facility.name for facility in self.facilities]

        # 获取所有的已完成的订单评论
        d["comments"] = []
        orders = Order.query.filter(Order.house_id == self.id,Order.status == "COMPLETE").order_by(Order.create_time.desc()).limit(HOUSE_VERBOSE_INFO_MAX_COMMENT)
        for order in orders:
            comment = {}
            comment['ctime'] = order.create_time.strftime("%Y-%m-%d %H:%M:%S")
            user_name = order.user.name if order.user.name != order.user.mobile else "匿名用户"
            comment['user_name'] = user_name
            comment['order_comment'] = order.comment
            d["comments"].append(comment)
        # 返回字典
        return d

class Facility(BaseModel, db.Model):
    """设施信息"""

    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字

    def to_dict(self):
        d={"id":self.id,"name":self.name}
        return d

class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)#房屋编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)# 下订单的用户编号
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)#预订的房间编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的起始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 预订的结束时间
    days = db.Column(db.Integer, nullable=False)  # 预订的总天数
    house_price = db.Column(db.Integer, nullable=False)  # 房屋的单价
    amount = db.Column(db.Integer, nullable=False)  # 订单的总金额
    status = db.Column(  # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单的评论信息或者拒单原因
    trade_no = db.Column(db.String(80))  # 交易的流水号 支付宝的
   
    def to_dict(self):
        d = {"order_id": self.id,
            "title": self.house.title,
            "img_url": AVATAR_URL_PREFIXED + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""}
        return d

