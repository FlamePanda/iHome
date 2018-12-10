#coding=utf-8

#-*- coding: UTF-8 -*-  

from ihome.libs.sms.CCPRestSDK import REST
import ihome.libs.sms.sms_config as sms_config

class SMS(object):
    '''短信验证码发送类'''
    _instance = None

    #主帐号
    accountSid= sms_config.accountSid

    #主帐号Token
    accountToken= sms_config.accountToken

    #应用Id
    appId= sms_config.appId

    #请求地址，格式如下，不需要写http://
    serverIP=sms_config.serverIP

    #请求端口
    serverPort=sms_config.serverPort

    #REST版本号
    softVersion=sms_config.softVersion

    def __new__(cls, *args, **kwargs):
        '''单例模式'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

      # 发送模板短信
      # @param to 手机号码
      # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
      # @param $tempId 模板Id
      # @return 发送成功 True 失败 False

    def sendTemplateSMS(self,to,datas,tempId):

        #初始化REST SDK
        rest = REST(self.serverIP,self.serverPort,self.softVersion)
        rest.setAccount(self.accountSid,self.accountToken)
        rest.setAppId(self.appId)

        result = rest.sendTemplateSMS(to,datas,tempId)
        if result.get('statusCode') == '000000':
            return True
        else:
            return False


if __name__ == '__main__':
    sms = SMS()
    res = sms.sendTemplateSMS('13551228724',['459857','5'],1)
    print(res)
   

