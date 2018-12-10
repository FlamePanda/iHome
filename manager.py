# 管理启动APP

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from ihome import create_app,db


# 创建APP
app = create_app('develop')
manager = Manager(app)
Migrate(app,db)
manager.add_command('db',MigrateCommand)

# 启动应用
if __name__ == "__main__":
	print('url_map:',app.url_map)
	manager.run()
	

'''
ihome 项目的启动命令,虚拟环境(python3.5)下
python manager.py runserver -h hostname -p port
ihome 项目SQLAlchemy操作命令（虚拟环境python3.5）。
python mamnger.py db init 初始化migrations。
python mamnger.py db migrate 生成迁移文件 类似于django的 makemigrations。
python mamnger.py db upgrade 生成数据库表。
python manager.py db history 查看当前的数据库版本信息。
'''
