# 处理项目的静态文件
from flask import Blueprint,current_app,make_response
from flask_wtf import csrf


html = Blueprint('html',__name__)


@html.route('/<re(r".*"):file_name>')
def static_html_handler(file_name):
	'''处理静态文件'''
	# 判断file_name是否为空，为空则赋值为index.html
	if not file_name:
		file_name = 'index.html'
	# 判断是否是favorite.con，若是返回icon
	if file_name == 'favicon.ico':
		return current_app.send_static_file('favicon.ico')
	# 设置响应的csrf的cookie
	response = make_response(current_app.send_static_file('html/'+file_name))
	csrf_token = csrf.generate_csrf()
	response.set_cookie('csrf_token',csrf_token)
	# 返回HTML所对应的页面静态文件
	return response
