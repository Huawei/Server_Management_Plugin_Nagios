#encoding:utf-8

#SNMP请求结果模型
class ChannelResult:
    
    def __init__(self, code = 0):
        self._code = 0;                 #SNMP请求错误码
        self._detail = "";              #具体提示信息
        self._data = {};                #请求数值（oid:value）
    
    def setResult(self, code, detail, data={}):
        self._code = code;
        self._detail = detail;
        self._data = data;
        
    def getCode(self):
        return self._code;
        
    def setCode(self, code):
        self._code = code;

    def getDetail(self):
        return self._detail;
        
    def setDetail(self, detail):
        self._detail = detail;
        
    def getData(self):
        return self._data;
        
    def setData(self, data):
        self._data = data;
    
    
#采集结果模型
class CollectResult:
    
    def __init__(self):
        
        self._hostName = "";           #host名称
        self._ipAddress = "";          #ip
        self._service = {};            #参加模块结果

    
    def getHostName(self):
        return self._hostName;
        
    def setHostName(self, hostName):
        self._hostName = hostName;
        
    def setIpAddress(self, ipAddress):
        self._ipAddress = ipAddress;

    def getIpAddress(self):
        return self._ipAddress;
    
    def getService(self):
        return self._service;
        
    def setService(self, service):
        self._service = service;
        
class ComponentResult:
    
    def __init__(self):
        self._component = None;        #采集模块信息
        self._result = None;           #SNMP请求结果
        
    def getComponent(self):
        return self._component;
        
    def setComponent(self, component):
        self._component = component;
        
    def getResult(self):
        return self._result;
        
    def setResult(self, result):
        self._result = result;
