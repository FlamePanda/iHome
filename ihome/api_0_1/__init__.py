# 蓝图初始化
from flask import Blueprint

#
api = Blueprint('api_1_0',__name__)



# 引入视图函数
from . import verify_code,passport,profile,houses,orders,pay

