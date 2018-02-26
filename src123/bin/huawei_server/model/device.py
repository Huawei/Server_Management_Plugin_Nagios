#encoding:utf-8


#配置
class Config:
    
    def __init__(self):
        
        self._deviceType = "";     #设备型号：Rack/HighDensity/E9000
        self._oid = "";            #设备类型OID节点
        self._file = [];
        
    def getDeviceType(self):
        return self._deviceType;
        
    def setDeviceType(self, deviceType):
        self._deviceType = deviceType;


    def getOid(self):
        return self._oid;
        
    def setOid(self, oid):
        self._oid = oid;
    
    def getFile(self):
        return self._file;
        
    def setFile(self, file):
        self._file = file;
        
#配置文件信息
class File:
    
    def __init__(self):
        
        self._type = "";
        self._name = ""; 
        self._replace = [];
        

    def getType(self):
        return self._type;
        
    def setType(self, type):
        self._type = type;

    def getName(self):
        return self._name;
        
    def setName(self, name):
        self._name = name;

    def getReplace(self):
        return self._replace;
        
    def setReplace(self, replace):
        self._replace = replace;   
#设备
class Device:
    
    def __init__(self):
        
        self._deviceType = "";      #设备型号：Rack/HighDensity/E9000
        self._deviceModel = "";     #设备类型
        self._components = {};      #设备组件
    
    
    def getDeviceType(self):
        return self._deviceType;
        
    def setDeviceType(self, deviceType):
        self._deviceType = deviceType;


    def getDeviceModel(self):
        return self._deviceModel;
        
    def setDeviceModel(self, deviceModel):
        self._deviceModel = deviceModel;
    
    def getComponents(self):
        return self._components;
        
    def setComponents(self, components):
        self._components = components;
        

#组件模块
class Component:
    
    def __init__(self):
        
        self._method = "";        #模块方法
        self._state = "";         #模块状态显示
        self._show = "";          #模块显示方式
        self._node = [];          #模块节点列表

    def getMethod(self):
        return self._method;
        
    def setMethod(self, method):
        self._method = method;

    def getState(self):
        return self._state;
        
    def setState(self, state):
        self._state = state;

    def setShow(self, show):
        self._show = show;
        
    def getShow(self):
        return self._show;

    def getNode(self):
        return self._node;
        
    def setNode(self, node):
        self._node = node;

        
#OID节点    
class Node:
    
    def __init__(self):
        self._name = "";          #名字
        self._value = "";
        self._oid = "";           #节点;
        self._range = "";         #节点范围(E9000)
        self._replace = {};         #节点值

    def getName(self):
        return self._name;
        
    def setName(self, name):
        self._name = name;
    
    def getValue(self):
        return self._value;
        
    def setValue(self, value):
        self._value = value;

    def getOid(self):
        return self._oid;
        
    def setOid(self, oid):
        self._oid = oid;

    def getRange(self):
        return self._range;
        
    def setRange(self, range):
        self._range = range;
        
    def getReplace(self):
        return self._replace;
        
    def setReplace(self, replace):
        self._replace = replace;