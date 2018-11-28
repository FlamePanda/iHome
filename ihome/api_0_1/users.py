# 用户视图类
from . import api
import logging
from ihome import models

#
@api.route('/index')
def index():
	return 'index page'
