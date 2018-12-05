# 存放项目的一些常量
# 项目注册页面常量

# 图片验证码过期时间
CAPTCHA_EXPIRE = 180

# 短信验证码的发送间隔
SMS_CAPTCHA_SEND_TIME = 60

# 短信验证码过期时间
SMS_CAPTCHA_EXPIRE = 60*5

# 用户登录的错误次数
USER_LOGIN_ERROR_NUMS = 5

# 用户登录错误到达次数后，禁止时间数
USER_PROHIBIT_LOGIN_TIME = 600

# FastFDFS的配置文件路径
from . import root_path
FASTFDFS_CONFIG_PATH = root_path+'/libs/fastfdfs/fdfs_client.conf'

# sms的配置
import sys 
sys.path.append(root_path+'/libs/sms')

# avatar url的前缀
AVATAR_URL_PREFIXED = 'http://192.168.232.135:8888/' 
