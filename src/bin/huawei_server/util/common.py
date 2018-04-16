#encoding:utf-8

import os
import sys
import time
import datetime
import commands
import re

from xml.etree import ElementTree

sys.path.append("..")
from base.logger import Logger
from constant.constant import *



class Common:
    _logger = Logger.getInstance()
    
    #获取执行脚本路径
    @classmethod
    def getExePath(cls):
        return os.path.normpath(sys.path[0]);

    #获取bin路径
    @classmethod
    def getBinPath(cls):
        return os.path.dirname(cls.getExePath());
    
    #获取etc路径
    @classmethod    
    def getEtcPath(cls):
        return os.path.dirname(cls.getBinPath()) + os.path.sep + "etc" + os.path.sep;

    #获取var路径
    @classmethod
    def getVarPath(cls):
        return os.path.dirname(cls.getBinPath()) + os.path.sep + "var" + os.path.sep;
 
    #获取nagios cmd路径
    @classmethod
    def getNagiosCmdPath(cls):
        nagioscmd_file =''
        initial_cfg = open(os.path.dirname(cls.getBinPath()) + os.path.sep + "etc" + os.path.sep+"huawei_server/initial.cfg")
        for pro in initial_cfg:
            if re.findall(r'^\s*nagios_cmd_file\s*=\s*/', pro):
                nagioscmd_file= re.sub(r'\s*$','',pro.split('=')[1])  
        if  not  nagioscmd_file == None:     
            return nagioscmd_file
        else :
            return ''    
    

    #获取插件配置文件路径
    @classmethod
    def getPluginConfigPath(cls):
        return cls.getEtcPath() + "huawei_server" + os.path.sep + "pluginConfig.xml";
    
    #获取Host配置文件路径
    @classmethod
    def getHostConfigPath(cls):
        return cls.getEtcPath() + "huawei_server" + os.path.sep + "huawei_hosts.xml";
    
    #获取设备配置文件路径
    @classmethod
    def getDeviceConfigPath(cls):
        return cls.getEtcPath() + "huawei_server" + os.path.sep + "device.xml";
    
    #获取具体设备配置文件路径
    @classmethod
    def getDeviceModelPath(cls):
        return cls.getEtcPath() + "huawei_server" + os.path.sep + "device";

    #获取跟节点
    @classmethod
    def getRoot(cls, path):
        try:
            tree = ElementTree.parse(path);
            return tree.getroot()
        except Exception, e:
            return None;

    
    #获取子节点
    @classmethod
    def getChild(cls, element):
        if element is not None:
            return [c for c in element];
        else:
            return None;
    
    #获取HOST的文件名称
    @classmethod
    def getFilePath(cls, path, hostName, ipAddress):
        if not os.path.exists(path):
            os.makedirs(path);
            
        return path + os.path.sep + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + "_" + hostName + " (%s)" % ipAddress + ".xml";
    
    #ElementTree缩进换行
    @classmethod
    def indent(cls, element, level=0):
        i = "\n" + level*"  "
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + "  "
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                cls.indent(element, level+1)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i
            
    
    #nagios.cmd文件数据写入
    @classmethod
    def writeCmd(cls, message):
        if not os.path.exists(cls.getNagiosCmdPath()):
            cls._logger.error("write cmd: nagios.cmd file is not exist.");
            return False;
        try:
            file = open(cls.getNagiosCmdPath(), 'a')
            file.write(message);
        except IOError, e:
            cls._logger.exception("write cmd: option file object exception:" % e);
            return False;
        finally:
            if 'file' in locals():  
                file.close(); 
        
        return True;
    
    #构建nagios消息
    @classmethod
    def constructMessage(cls, hostName, serviceName, status, information):
        
        return NAGIOS_CMD % (str(time.time()), hostName, serviceName, status, information);
    