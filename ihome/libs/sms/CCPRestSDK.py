    #-*- coding: UTF-8 -*-

from hashlib import md5
import base64
import datetime
from urllib.request import Request,urlopen
import json

class REST:
    
    AccountSid=''
    AccountToken=''
    AppId=''
    ServerIP=''
    ServerPort=''
    SoftVersion=''
    Iflog=False #是否打印日志
    Batch=''  #时间戳
    
    # 初始化
     # @param serverIP       必选参数    服务器地址
     # @param serverPort     必选参数    服务器端口
     # @param softVersion    必选参数    REST版本号
    def __init__(self,ServerIP,ServerPort,SoftVersion):

        self.ServerIP = ServerIP;
        self.ServerPort = ServerPort;
        self.SoftVersion = SoftVersion;
    
    
    # 设置主帐号
    # @param AccountSid  必选参数    主帐号
    # @param AccountToken  必选参数    主帐号Token
    
    def setAccount(self,AccountSid,AccountToken):
      self.AccountSid = AccountSid;
      self.AccountToken = AccountToken;   
    

    # 设置应用ID
    # 
    # @param AppId  必选参数    应用ID

    def setAppId(self,AppId):
       self.AppId = AppId; 
    
    def log(self,url,body,data):
        print('这是请求的URL：')
        print (url);
        print('这是请求包体:')
        print (body);
        print('这是响应包体:')
        print (data);
        print('********************************')
        
    # 发送模板短信
    # @param to  必选参数     短信接收彿手机号码集合,用英文逗号分开
    # @param datas 可选参数    内容数据
    # @param tempId 必选参数    模板Id
    def sendTemplateSMS(self, to,datas,tempId):

        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        #生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch;
        sig = md5(signature.encode('utf-8')).hexdigest().upper()
        #拼接URL
        url = "https://"+self.ServerIP + ":" + self.ServerPort + "/" + self.SoftVersion + "/Accounts/" + self.AccountSid + "/SMS/TemplateSMS?sig=" + sig
        #生成auth
        src = self.AccountSid + ":" + self.Batch;
        auth = (base64.b64encode(src.encode('utf-8'))).decode('utf-8')
        #创建包体
        b='['
        for a in datas:
            b+='"%s",'%(a) 
        b+=']'
        body = '''{"to": "%s", "datas": %s, "templateId": "%s", "appId": "%s"}'''%(to,b,tempId,self.AppId)
        data = bytes(body,encoding='utf8')
        req = Request(url=url,data=data)
        self.setHttpHeader(req)
        req.add_header("Authorization", auth)
        data = ''
        try:
            res = urlopen(req)
            data = res.read()
            res.close()
            #json格式
            locations = json.loads(data)
            if self.Iflog:
                self.log(url,body,data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url,body,data)
            return {'172001':'网络错误'}

    
    #主帐号鉴权
    def accAuth(self):
        if(self.ServerIP==""):
            print('172004')
            print('IP为空')
        
        if(int(self.ServerPort)<=0):
            print('172005')
            print('端口错误（小于等于0）')
        
        if(self.SoftVersion==""):
            print('172013')
            print('版本号为空')
        
        if(self.AccountSid==""):
            print('172006')
            print('主帐号为空')
        
        if(self.AccountToken==""):
            print('172007')
            print('主帐号令牌为空')
        
        if(self.AppId==""):
            print('172012')
            print('应用ID为空')



    #设置包头
    def setHttpHeader(self,req):
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
            
    
