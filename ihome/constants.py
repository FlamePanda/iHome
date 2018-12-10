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

# image url的前缀
AVATAR_URL_PREFIXED = 'http://192.168.232.135:8888/' 

# 设置城区（Area）信息的过期时间
AREAS_INFO_CACHE_EXPIRED = 3600

# 房屋详情页显示最多的评论数
HOUSE_VERBOSE_INFO_MAX_COMMENT = 20

# 首页展示轮播图的最大数量
INDEX_IMAGES_MAX_COUNT = 5

#首页图片数据保存时间
INDEX_IMAGES_EXPIRED = 7200

# 房屋详细信息保存时间
HOUSE_VERBOSE_EXPIRED = 24*60*60

# 显示查询的房源的数量
PER_PAGE_HOUSES_COUNT = 2

# 设置查询的房子的缓存时间
SEARCH_HOUSES_CACHE_EXPIRED = 7200

# 支付宝配置
import os
ALIPAY_APP_ID = "2016091900550211"
ALIPAY_APP_PRIVATE_KEY = os.path.join(os.path.dirname(__file__),"libs/paykeys/app_private_key.pem")
ALIPAY_PUBLIC_KEY = os.path.join(os.path.dirname(__file__),"libs/paykeys/app_alipay_public_key.pem")
ALIPAY_RESULT_URL = "http://192.168.232.135:5000/payComplete.html"
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?"
