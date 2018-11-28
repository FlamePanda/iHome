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

