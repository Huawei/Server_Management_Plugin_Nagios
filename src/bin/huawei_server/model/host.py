#encoding:utf-8


# 存储HOSt配置文档中设备登录信息 
class Host:
    
    def __init__(self):

        self._hostName = "";                #Host名称
        self._ipAddress = "";               #地址
        self._deviceType = "";              #设备型号
        self._collectVersion = "";          #SNMP采集版本
        self._port = 161;                   #SNMP监听端口
        self._userName = "";                #SNMP用户名
        self._password = "";                #SNMP密码
        self._authProtocol = "SHA";         #认证协议
        self._encryptionProtocol = "MD5";   #加密协议
        self._collectVersion = "";          #SNMP采集团体字;
        self._collectCommunity = "";        #SNMP采集团体字;
        self._alarmVersion = "";            #SNMP告警版本;
        self._alarmCommunity = "";          #SNMP告警团体字;
        self._collectBasic = [];            #Nagios框架采集的设备组件
        self._collectExtension = [];        #用户采集的设备组件

    
    def setHostName(self, hostName):
        self._hostName = hostName;

    def getHostName(self):
        return self._hostName;
    
    def setIpAddress(self, ipAddress):
        self._ipAddress = ipAddress;

    def getIpAddress(self):
        return self._ipAddress;

    def setDeviceType(self, deviceType):
        self._deviceType = deviceType;

    def getDeviceType(self):
        return self._deviceType;

    def setCollectVersion(self, collectVersion):
        self._collectVersion = collectVersion;

    def getCollectVersion(self):
        return self._collectVersion;

    def setPort(self, port):
        self._port = port;

    def getPort(self):
        return self._port;

    def setUserName(self, userName):
        self._userName = userName;

    def getUserName(self):
        return self._userName;

    def setPassword(self, password):
        self._password = password;

    def getPassword(self):
        return self._password;
    
    def setAuthProtocol(self, authProtocol):
        self._authProtocol = authProtocol;

    def getAuthProtocol(self):
        return self._authProtocol;

    def setEncryptionProtocol(self, encryptionProtocol):
        self._encryptionProtocol = encryptionProtocol;

    def getEncryptionProtocol(self):
        return self._encryptionProtocol;
    
    def setCollectCommunity(self, collectCommunity):
        self._collectCommunity = collectCommunity;

    def getCollectCommunity(self):
        return self._collectCommunity;
    
    def setAlarmVersion(self, alarmVersion):
        self._alarmVersion = alarmVersion;

    def getAlarmVersion(self):
        return self._alarmVersion;
    
    def setAlarmCommunity(self, alarmCommunity):
        self._alarmCommunity = alarmCommunity;

    def getAlarmCommunity(self):
        return self._alarmCommunity;
    
    def setCollectBasic(self, collectBasic):
        self._collectBasic = collectBasic;

    def getCollectBasic(self):
        return self._collectBasic;

    def setCollectExtension(self, collectExtension):
        self._collectExtension = collectExtension;

    def getCollectExtension(self):
        return self._collectExtension;

    