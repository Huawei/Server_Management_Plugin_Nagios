#encoding:utf-8

import os
import sys

import ConfigParser

import constInfo
import dataInfo

sys.path.append("..")
from util.common import Common
from model.host import Host
from base.logger import Logger

class ParseHostXml:
    _logger = Logger.getInstance(); 
       
    @classmethod
    def parseHostXml(cls, hostPath, hosts):
        
        if not os.path.exists(hostPath):
            cls._logger.error("parse host xml: file is not exist");
            return False;
        
        root = Common.getRoot(hostPath);
        if root is None:
            cls._logger.error("parser host xml: host xml format is not valid.");
            return False;     
        
        for node in Common.getChild(root):
            if "host" != node.tag:
                cls._logger.error("parser host xml: child node name is not host.");
                return False;
            
            host = Host();
            if not cls.__parseHostNode(node, host):
                cls._logger.error("parser host xml: host node format is not valid.");
                return False;
            hosts.append(host);
        
        return True;
        
    @classmethod
    def __parseHostNode(cls, node, host):
        
        elements = Common.getChild(node);
        if elements is None:
            cls._logger.error("parser host node: host node has no child node.");
            return False;
        
        for element in elements:
            if "device" == element.tag:
                if not cls.__parseDeviceNode(element, host):
                    return False;
            elif "collect" == element.tag:
                if not cls.__parseCollectNode(element, host):
                    return False;
            elif "alarm" == element.tag:
                if not cls.__parseAlarmNode(element, host):
                    return False;
            else:
                cls._logger.error("parser host node: host node should not has %s node." % element.tag);
                return False;
        
        return True;
            
    @classmethod    
    def __parseDeviceNode(cls, node, host):
        
        elements = Common.getChild(node);
        if elements is None:
            cls._logger.error("parser device node: device node has no child node.");
            return False;
        
        for element in elements:
            if "hostname" == element.tag:
                host.setHostName(element.text.strip());
            elif "ipaddress" == element.tag:
                host.setIpAddress(element.text.strip());
            elif "devicetype" == element.tag:
                host.setDeviceType(element.text.strip());
            elif "port" == element.tag:
                host.setPort(element.text.strip());
            else:
                cls._logger.error("parser device node: device node should not has %s node." % element.tag);
                return False;
           
        return True;
     
    @classmethod       
    def __parseCollectNode(cls, node, host):
         elements = Common.getChild(node);
         if elements is None:
            cls._logger.error("parser collect node: collect node has no child node.");
            return False;
        
         for element in elements:
            if "snmpversion" == element.tag:
                host.setCollectVersion(element.text.strip());
            elif "user" == element.tag:
                host.setUserName(element.text.strip());
            elif "pass" == element.tag:
                host.setPassword(cls.__dencrypt(element.text));
            elif "authprotocol" == element.tag:
                host.setAuthProtocol(element.text.strip());
            elif "privprotocol" == element.tag:
                host.setEncryptionProtocol(element.text.strip());
            elif "community" == element.tag:
                host.setCollectCommunity(cls.__dencrypt(element.text));          
            else:
                cls._logger.error("parser collect node: collect node should not has %s node." % element.tag);
                return False;           
         host.setCollectBasic(cls.__getDevcieCollect(host.getDeviceType(), "basic"));            
         host.setCollectExtension(cls.__getDevcieCollect(host.getDeviceType(), "extension")); 
         return True;
    
    @classmethod
    def __parseAlarmNode(cls, node, host):
        
         elements = Common.getChild(node);
         if elements is None:
            cls._logger.error("parser alarm node: alarm node has no child node.");
            return False;
        
         for element in elements:
            if "snmpversion" == element.tag:
                host.setAlarmVersion(element.text.strip());
            
            elif "community" == element.tag:
                host.setAlarmCommunity(cls.__dencrypt(element.text));
            else:
                pass         
         return True;
    
    @classmethod
    def __getDevcieCollect(cls, deviceType, collectType):
        
        if "Rack" == deviceType:
            
            if "basic" == collectType:
                return ["system", "power", "fan", "cpu", "memory", "hardDisk"];
            elif "extension" == collectType:
                return ["system", "power", "fan", "cpu", "memory", "hardDisk", "pCIe", "raid" , "logical", "component", "sensor", "firmwareVersion"];
                
        elif "HighDensity" == deviceType:
            
            if "basic" == collectType:
                return ["system", "power", "fan", "cpu", "memory", "hardDisk"];
            elif "extension" == collectType:
                return ["system", "power", "fan", "cpu", "memory", "hardDisk", "pCIe", "raid" , "logical", "component", "sensor", "firmwareVersion"];    
                
        elif "E9000" == deviceType:
            return ["system", "power", "fan", "switch", "blade"];
        
        else:
            cls._logger.error("get device collect failed, device type:%s." % deviceType);
            return []
    
     
    @classmethod
    def __readKey(cls):
        try:
            
            kfilepath = Common.getEtcPath() + 'huawei_server' + os.path.sep + 'configInfo.cfg'
            file = open(kfilepath, 'r')
            key = file.readline()
    
        except Exception, e:
            cls._logger.exception("read key: get key exception:%s." % e);
            return "";
        finally:
            if "file" in locals():
                if file is not None:
                     file.close()
            
        if key is not None :
            return key
        else:
            return constInfo.DATA_CONS
    
    @classmethod
    def __genRootKeyStr(cls):
        configfilepath = Common.getEtcPath() + 'huawei_server' + os.path.sep + 'initial.cfg'
        parser = ConfigParser.ConfigParser()
        configdata = {}
        rootkey = ""
        try:
            file = open(configfilepath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    configdata[key] = value
            rootkey = configdata.get("nagios_costant3")
            
        except Exception, e:
            cls._logger.exception("read root key: get root key exception:%s." %  e);
            return "";
        finally:
            if file is not None:
                file.close()
            
    
        if rootkey is not None :
            key = dataInfo.CONSTANT1 + rootkey + constInfo.CONSTANT2
            return key
        else:
            return ""   
   
    @classmethod 
    def __dencryptKey(cls, pkey, rootkey):
        
        if rootkey is not None:
            encryptStr = os.popen("echo " +  "'" + pkey + "'" +  " | openssl aes-256-cbc -d -k " +  "'" + rootkey + "'" +  " -base64")\
                                            .read().strip()
        return encryptStr       
    
    @classmethod
    def __dencrypt(cls, str):
        '''
        ' aes解密，依赖linux平外，依赖openssl
        '''
        key = cls.__readKey()
        rootKey = cls.__genRootKeyStr()
         
        k = cls.__dencryptKey(key, rootKey)
         
        dencryptStr = os.popen("echo " +  "'" + str + "'" +  " | openssl aes-256-cbc -d -k " + "'" +  k + "'" +  " -base64")\
                                .read().strip()
                       
        if dencryptStr is None or dencryptStr == '':
            return ''
        if dencryptStr == str:
            return ''
        return dencryptStr
    