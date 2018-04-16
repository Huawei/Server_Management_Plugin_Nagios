#encoding:utf-8

import sys

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity import config
from pysnmp.error import PySnmpError


from logger import Logger

sys.path.append("..")
from model.host import Host
from model.result import ChannelResult
from constant.constant import *

Authentication = {
            "SHA": config.usmHMACSHAAuthProtocol,
            "MD5": config.usmHMACMD5AuthProtocol,
            }

Encryption = {              
            "AES": config.usmAesCfb128Protocol,
            "DES": config.usmDESPrivProtocol,
            }

#SNMP通道类
class Channel:
    
    _logger = Logger.getInstance();
    
    def __init__(self, host, timeout = 10, retries = 2):
        
        self._channel = cmdgen.CommandGenerator();        
        
        try:
            self._target = cmdgen.UdpTransportTarget((host.getIpAddress(), 
                                                      int(host.getPort())), 
                                                      timeout = timeout, 
                                                      retries = retries);
        except PySnmpError,e:
            self._target = None;
            self._logger.exception("channel init: create udp target exception:%s."  % e);
            
        
        if "v3" == host.getCollectVersion().lower():
            self._userData =  cmdgen.UsmUserData(host.getUserName(), 
                                                 host.getPassword(),
                                                 host.getPassword(),
                                                 Authentication[host.getAuthProtocol()], 
                                                 Encryption[host.getEncryptionProtocol()]);
                                                 
        elif "v1" == host.getCollectVersion().lower() or "v2" == host.getCollectVersion().lower(): 
            self._userData = cmdgen.CommunityData(host.getCollectCommunity());
        else :
            self._userData = None;
                    
    
    def getCmd(self, *oid):

        result = ChannelResult();
        
        if self._target is None:
            return result.setResult(NAGIOS_ERROR_INVALID_TARGET, "");
        
        errorIndication, errorStatus, errorIndex, varBinds = self._channel.getCmd(
                                                                           self._userData,
                                                                           self._target,
                                                                           *oid)


        # Check for errors and print out results
        if errorIndication:
            self._logger.exception("get cmd: get oid info error:%s." % errorIndication);
            result.setResult(NAGIOS_ERROR_FAILED, errorIndication);
        else:
            if errorStatus:
                 self._logger.exception("get cmd: get oid info error:%s." % varBinds[int(errorIndex)-1][0]);
                 result.setResult(NAGIOS_ERROR_INVALID_ENGINE, varBinds[int(errorIndex)-1][0]);
            else:
                
                data = {};
                for name, value in varBinds:
                    data[name.prettyPrint()] = value.prettyPrint();
                
                result.setResult(NAGIOS_ERROR_SUCCESS, "", data);
            
        return  result;
    
    def bulkCmd(self, nonRepeaters, maxRepetitions, *oid):
        
        result = ChannelResult();
        
        if self._target is None:
            return result.setResult(NAGIOS_ERROR_INVALID_TARGET, "");
        
        errorIndication, errorStatus, errorIndex, varBindTable = self._channel.bulkCmd(
                                                                                self._userData,
                                                                                self._target,
                                                                                nonRepeaters,
                                                                                maxRepetitions,
                                                                                *oid)
        
        if errorIndication:
            self._logger.exception("bulk cmd: get oid info error:%s." % errorIndication);
            result.setResult(NAGIOS_ERROR_FAILED ,errorIndication);
            
        else:
            if errorStatus:
                self._logger.exception("bulk cmd: get oid info error:%s." % varBinds[int(errorIndex)-1][0]);
                result.setResult(NAGIOS_ERROR_INVALID_ENGINE, varBinds[int(errorIndex)-1][0]);
            else:
                data = {};
                for varBindTableRow in varBindTable:
                    for name, value in varBindTableRow:
                        
                        if not self.__filter(name.prettyPrint(), *oid):
                            continue;
                        
                        data[name.prettyPrint()] = value.prettyPrint();
                
                result.setResult(NAGIOS_ERROR_SUCCESS, "", data);
                    
        return result      
    
    
    def __filter(self, name, *oid):
        
        for item in oid:
            if name.startswith(item + "."):
                return True;
        
        return False;
            
            
            
            
        
        
    