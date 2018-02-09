#coding=utf-8


############## PLUGIN VERSION ###########################

VERSTION_STR ="HUAWEI PLUGIN V1.0.3" 
################################################
'''
Created on 2018-1-18

'''

import sys
import os
import re
import commands
import ConfigParser
from xml.dom import minidom
from datetime import datetime 
from genKey import *
from optparse import OptionParser
import time

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACMD5AuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmDESPrivProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACSHAAuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmAesCfb128Protocol
from pysnmp.entity import config
from pysnmp.error import PySnmpError
from xml.dom import minidom
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import OctetString, IpAddress
from pysnmp.proto.rfc1902 import Integer
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.api import v2c


DEBUG=False 
def debugPrint( StrforPrint ):
    if DEBUG == True:
        print StrforPrint
    else:
        pass 

#+++++++++++++const for cmd options ++++++++++++++++++++++++++++
CFG_NODE_KEY_HOST_NAME="hostName"
CFG_NODE_KEY_DEVTYPE ="type"
CFG_NODE_KEY_PPORT ="port"
CFG_NODE_KEY_CSNMPVERSION ="CSnmp"
CFG_NODE_KEY_CUSER ="CUser"
CFG_NODE_KEY_CPWD ="CPass"
CFG_NODE_KEY_CAUTH ="CAuth"
CFG_NODE_KEY_CPRIV ="CPriv"
CFG_NODE_KEY_CCNMTY="Ccommunity"
CFG_NODE_KEY_TSNMPVERSION ="TSnmp"
CFG_NODE_KEY_TUSER="TUser"
CFG_NODE_KEY_TPWD="TPass"
CFG_NODE_KEY_TAUTH="TAuth"
CFG_NODE_KEY_TPRIV="TPriv"
CFG_NODE_KEY_TCNMTY="Tcommunity"
CFG_NODE_KEY_IP="IP"
OPTION_CMD_LIST=[CFG_NODE_KEY_IP,CFG_NODE_KEY_HOST_NAME,CFG_NODE_KEY_DEVTYPE,CFG_NODE_KEY_PPORT,CFG_NODE_KEY_CSNMPVERSION,CFG_NODE_KEY_CUSER,CFG_NODE_KEY_CPWD,CFG_NODE_KEY_CAUTH,CFG_NODE_KEY_CPRIV,CFG_NODE_KEY_CCNMTY,CFG_NODE_KEY_TSNMPVERSION,CFG_NODE_KEY_TUSER,CFG_NODE_KEY_TPWD,CFG_NODE_KEY_TAUTH,CFG_NODE_KEY_TPRIV,CFG_NODE_KEY_TCNMTY]
#--------------------ends cmd options ----------------------------------     
        
#------------------------- cmds -------------------------------------        
NAME_FUNTION_ADD="ADD"
NAME_FUNTION_BATCH="BATCH"
NAME_FUNTION_DEL="DEL"
NAME_FUNTION_INQUIRY="INQUIRY"
NAME_FUNTION_VERSION="VERSION" 
NAME_FUNTION_RESETSERVER="RESETSERVER"
CMD_LIST=[NAME_FUNTION_ADD,NAME_FUNTION_BATCH,NAME_FUNTION_DEL,NAME_FUNTION_INQUIRY,NAME_FUNTION_VERSION,NAME_FUNTION_RESETSERVER]
#-------------------------funtion cmd-------------------------------------     
#+++++++++++++const for xml parse  ++++++++++++++++++++++++++++
HOST_CFG_KEY_DEVICETYPE = 'devicetype'
HOST_CFG_KEY_PORT = 'port'
HOST_CFG_KEY_HOST = 'host'
HOST_CFG_KEY_HOSTNAME = 'hostname'
HOST_CFG_KEY_COLLECT = 'collect'
HOST_CFG_KEY_ALARM = 'alarm'
HOST_CFG_KEY_DEVICE = 'device'
HOST_CFG_KEY_IP = 'ipaddress'
HOST_CFG_KEY_NAME = 'name'
HOST_CFG_KEY_USER = 'user'
HOST_CFG_KEY_PASS = 'pass'
HOST_CFG_KEY_AUTHPROTOCOL = 'authprotocol'
HOST_CFG_KEY_PRIVPROTOCOL = 'privprotocol'
HOST_CFG_KEY_COMMUNITY = 'community'
HOST_CFG_KEY_SNMPVERSION = 'snmpversion'
HOST_CFG_KEY_TRAPSNMPVERSION = 'snmpversion'
HOST_CFG_KEY_TRAPCOMMUNITY = 'community'
HOST_CFG_KEY_TYPE = 'type'
#--------------------ends xml parse----------------------------------



#--------------------cfg for oid -------------------------
SERVER_TYPE_OID_KEY = 'server_type_oid'
SERVER_TRAP_SETTING_IP_BMC_KEY = 'server_trap_setting_ip_bmc'
SERVER_TRAP_SETTING_PORT_BMC_KEY = 'server_trap_setting_port_bmc'
SERVER_TRAP_SETTING_ENABLE_BMC_KEY = 'server_trap_setting_enable_bmc'
SERVER_TRAP_SETTING_USER_BMC_KEY='server_trap_setting_user_bmc'
SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY='server_trap_setting_trapversion_bmc'
SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY='server_trap_setting_trapmode_bmc'
SERVER_TRAP_SETTING_COMMUNITY_BMC_KEY='server_trap_setting_trapcommunity_bmc'                                     
SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY='server_trap_setting_trapenable_bmc'
SERVER_TRAP_SETTING_IP_SMM_KEY = 'server_trap_setting_ip_smm'
SERVER_TRAP_SETTING_PORT_SMM_KEY = 'server_trap_setting_port_smm'
SERVER_TRAP_SETTING_ENABLE_SMM_KEY = 'server_trap_setting_enable_smm'
SERVER_TRAP_SETTING_USER_SMM_KEY="server_trap_setting_user_smm"
SERVER_TRAP_SETTING_VERSION_SMM_KEY="server_trap_setting_version_smm"
SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY="server_trap_setting_format_smm"
SERVER_TRAP_SETTING_COMMUNITY_SMM_KEY="server_trap_setting_community_smm"

#--------------------------end cfg for oid ------------------------

#--------------------------------const oid Key -----------

### -----------Exception define ----------------------------------
class pareExcept(Exception):
    pass 

class IPExcept(Exception):
    pass 

#---------------------------------end 
 
def main():
    MSG_USAGE = ''' add   %prog add -i IPADDRESS [] ..
                    batch %prog batch -i IPADDRESS [] ..
                    del  %prog del -i IPADDRESS [] ..
                    inquiry   %prog inquiry
                    version %prog version
                    resetserver %prog resetserver -i IPADDRESS [] ..                  
                '''
    optParser = OptionParser(MSG_USAGE)
                  
    optParser.add_option("-i", "--ip"
                         , dest="ip"
                         , help=" IP address "
                         + "example:192.168.1.1, 192.168.2.* ,192.168.1-10"
                         ,default=None
                        )
                        
    optParser.add_option("-H", "--hostName"
                         , dest=CFG_NODE_KEY_HOST_NAME
                         , help="name of devices"
                         + "default: hostname = ipaddr"
                         ,default=None
                        )
    optParser.add_option("-t", "--type"
                         , dest=CFG_NODE_KEY_DEVTYPE
                         , help="deviceType,suppport :Rack Blade HighDensity default: Rack" 
                         ,default="Rack"
                         )
    optParser.add_option("-p", "--port"
                         , dest=CFG_NODE_KEY_PPORT
                         , help="snmp service Port"
                         + "default: 161"
                         ,default="161"
                        )
    optParser.add_option("-v", "--CSnmp"
                         , dest=CFG_NODE_KEY_CSNMPVERSION
                         , help="SnmpVersion for collecting infomation celloct"
                         + "example: v1,v2,v3"
                         ,default="v3"
                        )
    optParser.add_option("-u", "--CUser"
                         , dest=CFG_NODE_KEY_CUSER
                         , help="Snmp user  for collecting infomation celloct"
                         + ""
                         ,default=None
                        ) 
    optParser.add_option("-a", "--CPass"
                        , dest=CFG_NODE_KEY_CPWD
                        , help="Snmp passwd for collecting infomation celloct "
                        + ""
                        ,default=None
                        )
    optParser.add_option("-x", "--CAuth"
                         , dest=CFG_NODE_KEY_CAUTH
                         , help="authprotocol of snmp to collect infomation; options:MD5|SHA"
                         + ""
                         ,default="SHA"
                        ) 
    optParser.add_option("-d", "--CPriv"
                         , dest=CFG_NODE_KEY_CPRIV
                         , help="privprotocol of snmp to collect infomation ; options:AES|DES"
                         + ""
                         ,default="AES"
                        )
    optParser.add_option("-c", "--Ccommunity"
                         , dest=CFG_NODE_KEY_CCNMTY
                         , help="community of snmp to collect infomation "
                         + ""
                         ,default=None
                        )
    optParser.add_option("-V", "--TSnmp"
                         , dest=CFG_NODE_KEY_TSNMPVERSION
                         , help="SnmpVersion to get trap"
                         + "example: v1,v2,v3"
                         ,default="v3"
                        )
    optParser.add_option("-U", "--TUser"
                         , dest=CFG_NODE_KEY_TUSER
                         , help="Snmp user  to get trap"
                         + ""
                         ,default=None
                        ) 
    optParser.add_option("-A", "--TPass"
                        , dest=CFG_NODE_KEY_TPWD
                        , help="  Snmp passwd to get trap "
                        + ""
                        ,default=None
                        )
    optParser.add_option("-X", "--TAuth"
                         , dest=CFG_NODE_KEY_TAUTH
                         , help="authprotocol of snmp to get trap ;options:MD5|SHA"
                         + ""
                         ,default=None
                        ) 
    optParser.add_option("-D", "--TPriv"
                         , dest=CFG_NODE_KEY_TPRIV
                         , help="privprotocol of snmp to get trap ;options:AES|DES "
                         + ""
                         ,default=None
                        )
    optParser.add_option("-C", "--Tcommunity"
                         , dest=CFG_NODE_KEY_TCNMTY
                         , help="community of snmp to get trap"
                         + ""
                         ,default=None
                        )  
                            
    options, args = optParser.parse_args()

    if not len(args)==1:
        optParser.print_help()
        return 
    if args[0].upper() not in CMD_LIST:
        optParser.print_help()
        return 
    if args[0].upper() in [ NAME_FUNTION_ADD, NAME_FUNTION_BATCH ]:
        if options.ip == None :
            print "IP mush be set "
            return 
        if options.CUser == None and options.CSnmp.lower()=='v3':
            print "when use SNMP v3 user mush be set "          
            return 
        if options.CPass == None and options.CSnmp.lower()=='v3':
            print "when use SNMP v3 user mush be set "
            return
        if options.Ccommunity == None and options.CSnmp.lower() in['v2','v1']:
            print "when use SNMP v2 v1 community mush be set "
            return 
        if  options.CAuth is not None :
            if options.CAuth.upper() not in ["MD5","SHA"]   :
                print "please check -x"
                optParser.print_help()
                return
            else: 
                options.CAuth=options.CAuth.upper()                
        if  options.CPriv is not None :
            if options.CPriv.upper() not in ["AES","DES"]  :
                print "please check -d"
                optParser.print_help()
                return
            else:
                options.CPriv=options.CPriv.upper()
        if  options.TAuth is not None :
            if options.TAuth.upper() not in ["MD5","SHA"] :
                print "please check -X"
                optParser.print_help()
                return
            else:
                options.TAuth = options.TAuth.upper()             
        if  options.TPriv is not None :
            if options.TPriv.upper() not in ["AES","DES"]  :
                print "please check -D"
                optParser.print_help()
                return 
            else:
                options.TPriv = options.TPriv.upper()              
        if  options.CSnmp is not None :
            if options.CSnmp.lower() not in ["v1","v2","v3"]  :
                print "please check -v "
                optParser.print_help()
                return 
            else :
                options.CSnmp = options.CSnmp.lower()             
        if  options.TSnmp is not None :
            if options.TSnmp.lower() not in ["v1","v2","v3"]  :
                print "please check -V"
                optParser.print_help()
                return 
            else:
                 options.TSnmp =  options.TSnmp.lower()
        if options.type is not None :
            if options.type.upper() not in [ "RACK","BLADE","HIGHDENSITY"]  : 
                print "please check -t,only suppport :Rack Blade HighDensity" 
            else:
                if  options.type.upper() == "RACK":
                    options.type = "Rack"  
                if  options.type.upper() == "BLADE": 
                    options.type = "Blade"    
                if  options.type.upper() == "HIGHDENSITY": 
                    options.type = "HighDensity"                     
        #batch set hostName cant be set
        if  options.hostName is not None and args[0].upper() == NAME_FUNTION_BATCH  :
            print  "Info: when batch  hostName would auto be set as ip address "
            options.hostName=None               
    ConfigHandler(parseParm(options, args)).mainHandler()        
        
    
        
def parseParm(options, args):
    _snmpMaplist={CFG_NODE_KEY_TSNMPVERSION:CFG_NODE_KEY_CSNMPVERSION,CFG_NODE_KEY_TUSER:CFG_NODE_KEY_CUSER,CFG_NODE_KEY_TPWD:CFG_NODE_KEY_CPWD,CFG_NODE_KEY_TAUTH:CFG_NODE_KEY_CAUTH,CFG_NODE_KEY_TPRIV:CFG_NODE_KEY_CPRIV,CFG_NODE_KEY_TCNMTY:CFG_NODE_KEY_CCNMTY}
    parmlist= {
                "fun":args[0],
                OPTION_CMD_LIST[0] :options.ip,
                OPTION_CMD_LIST[1] :options.hostName,
                OPTION_CMD_LIST[2] :options.type,
                OPTION_CMD_LIST[3] :options.port,
                OPTION_CMD_LIST[4] :options.CSnmp,
                OPTION_CMD_LIST[5] :options.CUser,
                OPTION_CMD_LIST[6] :options.CPass,
                OPTION_CMD_LIST[7] :options.CAuth,
                OPTION_CMD_LIST[8] :options.CPriv,
                OPTION_CMD_LIST[9] :options.Ccommunity,
                OPTION_CMD_LIST[10] :options.TSnmp,
                OPTION_CMD_LIST[11] :options.TUser,
                OPTION_CMD_LIST[12] :options.TPass,
                OPTION_CMD_LIST[13] :options.TAuth,
                OPTION_CMD_LIST[14] :options.TPriv,
                OPTION_CMD_LIST[15] :options.Tcommunity, 
               }    
    #if SNMP config for Trap is none then use the collect snmp config 
    for _tmpitem in _snmpMaplist.keys() :
        if parmlist[_tmpitem] == None :
            parmlist[_tmpitem] =parmlist[ _snmpMaplist[_tmpitem] ]
    
    return  parmlist  
         
class commonFun():
    @classmethod
    def matchSigleIp(cls,ipAddstr):
        matcher = re.match( "((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)", ipAddstr )
        if not matcher is None:
            if matcher.group(0) == ipAddstr :
                return True 
            else :
                return False    
        else:
            return False 
    @classmethod        
    def matchBatchIP(cls,ipAddstr):
        ipList=[]
        matcher = re.match("(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)\*",ipAddstr)  
        if  not matcher is None:
            ipStr = matcher.group(1)+matcher.group(2)+matcher.group(3)  
            for i in range(255):
                ipList.append( ipStr+str(i) )          
            return True,ipList
        else:
            matcher = re.match("(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?\.)(2[0-4]\d|25[0-5]|[01]?\d\d?)-(2[0-4]\d|25[0-5]|[01]?\d\d?)",ipAddstr)  
            if not matcher is None:
                ipStr = matcher.group(1)+matcher.group(2)+matcher.group(3)
                startStr=matcher.group(4)
                endStr=matcher.group(5)
                if int (endStr) < int (startStr):
                    for i in range(255):
                        if i < int(endStr):
                            continue
                        if i> int(startStr):
                            continue           
                        ipList.append(ipStr+str(i))                       
                else:
                    for i in range(255):
                        if i < int(startStr):
                            continue
                        if i > int(endStr):
                            continue           
                        ipList.append(ipStr+str(i))    
                return True, ipList      
            else: 
                return  False,ipList   
 
class ConfigHandler():
    def __init__(self,argv):
        self.__parm=argv
        self.__configDiclist=[] 
        self.__trapPort=""
        self.__localip=""
        self.CofnigServer=False
        self.__OidDic={}
        self._nagiosHomeDir=self.__find_nagiosdir()
        self.__pareHostFile()
        self.__PareInitFile()
        self.__ParePluginFile()
    def __ParePluginFile(self):
        _etcPath=self.__getCfgPath()
        filePath=_etcPath+ os.path.sep + "huawei_plugin.cfg" 
        parser = ConfigParser.ConfigParser()
        file=None
        try:
            file = open(filePath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                if not section.upper()== "GENERIC":
                    continue 
                for (key, value) in parser.items(section):
                        self.__OidDic[key] = value             
        except Exception,err :   
            print "__ParePluginFile err",str(err)  
        finally:
            if file is not None:
                file.close() 
                
    def  __PareInitFile(self): 
        _etcPath=self.__getCfgPath()
        filePath=_etcPath+ os.path.sep + "initial.cfg" 
        parser = ConfigParser.ConfigParser()
        file=None
        try:
            file = open(filePath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    if key == "local_address": 
                        self.__localip=value
                    elif key=="listen_port":
                        self.__trapPort=value               
                    else:
                        continue
        except Exception,err :   
            print "__PareInitFile err",str(err)  
        finally:
            if file is not None:
                file.close()        
  
    def __pareHostFile(self):   
        _etcPath=self.__getCfgPath()
        filePath=_etcPath+ os.path.sep + "huawei_hosts.xml"
        if os.path.exists(filePath) == False :
            print filePath + "not exist",
            return False
        file=None    
        file = open(filePath, 'r')
        doc = minidom.parseString(file.read()) 
        for hostnode in doc.documentElement.getElementsByTagName(HOST_CFG_KEY_HOST):
            try: 
                parmDic = {}
                for node in hostnode.childNodes:
                    if  node.nodeName==HOST_CFG_KEY_DEVICE:
                        parmDic[CFG_NODE_KEY_HOST_NAME] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_HOSTNAME)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                        parmDic[HOST_CFG_KEY_IP] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_IP)[0]\
                                  .childNodes[0] \
                                  .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_DEVTYPE] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_DEVICETYPE)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_PPORT] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_PORT)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                    elif  node.nodeName==HOST_CFG_KEY_ALARM:
                        parmDic[CFG_NODE_KEY_TUSER] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_USER)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_TPWD] = \
                                   self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_PASS)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_TSNMPVERSION] = \
                                    str(node.getElementsByTagName(HOST_CFG_KEY_TRAPSNMPVERSION)[0]\
                                    .childNodes[0]\
                                    .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_TCNMTY] = \
                                     self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_TRAPCOMMUNITY)[0]\
                                     .childNodes[0]\
                                     .nodeValue.strip()))
                        if node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL).length != 0:
                               parmDic[CFG_NODE_KEY_TAUTH] = \
                                           str(node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL)[0]\
                                           .childNodes[0] \
                                           .nodeValue.strip())
                        else:
                                parmDic[CFG_NODE_KEY_TAUTH] = "SHA"
                        if node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL).length != 0:
                                parmDic[CFG_NODE_KEY_TPRIV] = \
                                            str(node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL)[0]\
                                            .childNodes[0] \
                                            .nodeValue.strip())
                        else:
                                parmDic[CFG_NODE_KEY_TPRIV] = "AES" 
                    elif  node.nodeName==HOST_CFG_KEY_COLLECT:
                        parmDic[CFG_NODE_KEY_CUSER] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_USER)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_CPWD] = \
                                   self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_PASS)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip()))
                        parmDic[CFG_NODE_KEY_CSNMPVERSION] = \
                                    str(node.getElementsByTagName(HOST_CFG_KEY_TRAPSNMPVERSION)[0]\
                                    .childNodes[0]\
                                    .nodeValue.strip())
                        parmDic[CFG_NODE_KEY_CCNMTY] = \
                                     self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_TRAPCOMMUNITY)[0]\
                                     .childNodes[0]\
                                     .nodeValue.strip()))
                        if node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL).length != 0:
                               parmDic[CFG_NODE_KEY_CAUTH] = \
                                           str(node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL)[0]\
                                           .childNodes[0] \
                                           .nodeValue.strip())
                        else:
                                parmDic[CFG_NODE_KEY_CAUTH] = "SHA"
                        if node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL).length != 0:
                                parmDic[CFG_NODE_KEY_CPRIV] = \
                                            str(node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL)[0]\
                                            .childNodes[0] \
                                            .nodeValue.strip())
                        else:
                                parmDic[CFG_NODE_KEY_CPRIV] = "AES"                                     
                    else:
                        continue       
                tmpDic={} 
                keyStr=None
                if parmDic.has_key(HOST_CFG_KEY_IP):           
                    keyStr=parmDic.pop(HOST_CFG_KEY_IP)               
                tmpDic.update(parmDic)
                tmphostDic={}
                if keyStr is not None:
                    tmphostDic[keyStr]=tmpDic 
                    self.__configDiclist.append(tmphostDic)
            except Exception , err:
                print "__pareHostFile except err : %s"%(str(err))           
        if file is not None:
            file.close()           
        return True
		 
    def mainHandler(self): 
        _funDis={ 
                    NAME_FUNTION_ADD:self.funAdd,
                    NAME_FUNTION_BATCH:self.funBatch,
                    NAME_FUNTION_DEL:self.funDel,
                    NAME_FUNTION_INQUIRY:self.funInquiry,
                    NAME_FUNTION_VERSION:self.funVersion, 
                    NAME_FUNTION_RESETSERVER:self.funReSetServer,                    
                }   
        try :                
            _funDis[ self.__parm["fun"].upper()]()            
            self.creatConfigfile()
            if self.CofnigServer is True:
                self.funSetServer()
            self.addPlugincfgInNagios()
            self.restartNagios()    
        except  IPExcept :
            print " please check IP "
        except Exception,err:
            print " mainHandler Exception  error info:" , str(err)     
    # set server ip ,port ,snmp config for trap         
    def funSetServer (self): 
        print "start set Server Trap config"
        ret =None
        iPlist = []
        for list in  self.__configDiclist:
            try:    
                for ipaddress, hostdic in list.items():
                    if hostdic[CFG_NODE_KEY_CUSER] is None:
                        print " set server error ipaddress:%s has no snmpUser "%(ipaddress)      
                        return ret,iPlist                   
                    if hostdic[CFG_NODE_KEY_CPWD] is None:
                        print " set server error ipaddress:%s has no pwd "%(ipaddress)      
                        return ret,iPlist              
                    errorIndication = None
                    errorStatus = 0
                    errorIndex = 0
                    varBinds = None
                    if 'SHA'.find(str(hostdic[CFG_NODE_KEY_CAUTH].upper())) != -1:
                        authProtocol = usmHMACSHAAuthProtocol
                    else:
                        authProtocol = usmHMACMD5AuthProtocol
                    if 'AES'.find(str(hostdic[CFG_NODE_KEY_CPRIV].upper())) != -1:
                        privProtocol = usmAesCfb128Protocol
                    else:
                        privProtocol = usmDESPrivProtocol
                    useData= cmdgen.UsmUserData(hostdic[CFG_NODE_KEY_CUSER], \
                                                       hostdic[CFG_NODE_KEY_CPWD], \
                                                       hostdic[CFG_NODE_KEY_CPWD], \
                                                       authProtocol, \
                                                       privProtocol)

                    #get server type
                    type =None
                    type = self._getServerType (ipaddress,useData,hostdic[CFG_NODE_KEY_PPORT])                        
                    if type is None:       
                        print "server:%s  get server type error "%ipaddress  
                        print "server:%s can not  set trap config ,please set it yourself "%ipaddress
                        iPlist.append(ipaddress)                        
                        continue        
                    print "--------------------------------------------------"
                    print "server:%s the last trap ip will be  set "%ipaddress
                    print "server:%s trap mode will be set to eventcode mode "%ipaddress
                                       
                    if  "E9000" in str(type) or "E6000" in str(type):
                        localaddresssetted = IpAddress(self.__localip)
                        portsetted = OctetString(self.__trapPort)
                        enableoid =Integer(1)
                        #eventCodeMode
                        trapmode= Integer(0)  
                       
                        if 'V3'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                            print "server:%s trap SNMP user will be set "%ipaddress                       
                            trapuser=OctetString(hostdic[CFG_NODE_KEY_CUSER])
                            trapversion=OctetString("v3") 
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                    cmdgen.CommandGenerator().setCmd(\
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,hostdic[CFG_NODE_KEY_PPORT])),\
                                   (self.__OidDic[SERVER_TRAP_SETTING_USER_SMM_KEY], trapuser))      
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                    cmdgen.CommandGenerator().setCmd(\
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress,hostdic[CFG_NODE_KEY_PPORT])),\
                                    (self.__OidDic[SERVER_TRAP_SETTING_IP_SMM_KEY], localaddresssetted),  
                                    (self.__OidDic[SERVER_TRAP_SETTING_PORT_SMM_KEY], portsetted),  
                                    (self.__OidDic[SERVER_TRAP_SETTING_ENABLE_SMM_KEY], enableoid),  
                                    (self.__OidDic[SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY], trapmode),                              
                                    (self.__OidDic[SERVER_TRAP_SETTING_VERSION_SMM_KEY], trapversion)) 
                        else:
                            print "server:%s trap comunity will be set "%ipaddress
                            if 'V2'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion=OctetString("v2c")
                               
                            if 'V1'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion= OctetString("v1")
                            trapComunity=OctetString(hostdic[CFG_NODE_KEY_TCNMTY])
                            errorIndication, errorStatus, errorIndex, varBinds = \
                            cmdgen.CommandGenerator().setCmd(\
                                    useData,
                                    cmdgen.UdpTransportTarget((ipaddress, \
                                                               hostdic[CFG_NODE_KEY_PPORT])),
                                    (self.__OidDic[SERVER_TRAP_SETTING_IP_SMM_KEY], localaddresssetted),  
                                    (self.__OidDic[SERVER_TRAP_SETTING_PORT_SMM_KEY], portsetted),  
                                    (self.__OidDic[SERVER_TRAP_SETTING_ENABLE_SMM_KEY], enableoid), 
                                    (self.__OidDic[SERVER_TRAP_SETTING_VERSION_SMM_KEY], trapversion), 
                                    (self.__OidDic[SERVER_TRAP_SETTING_COMMUNITY_SMM_KEY], trapComunity), 
                                    (self.__OidDic[SERVER_TRAP_SETTING_TRAPMODE_SMM_KEY], trapmode))
                    else:
                        #ibmc 
                        localaddresssetted = OctetString(self.__localip)
                        portsetted = Integer(self.__trapPort)
                        enableoid =Integer(2)
                        enableAll=Integer(2)
                        #eventCodeMode
                        trapmode= Integer(1)  
                        if 'V3'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                            print "server:%s trap SNMP user will be set "%ipaddress  
                            trapuser=OctetString(hostdic[CFG_NODE_KEY_CUSER])
                            trapversion=Integer(3)            
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(\
                                        useData,
                                        cmdgen.UdpTransportTarget((ipaddress,hostdic[CFG_NODE_KEY_PPORT])),
                                        (self.__OidDic[SERVER_TRAP_SETTING_IP_BMC_KEY], localaddresssetted),  
                                        (self.__OidDic[SERVER_TRAP_SETTING_PORT_BMC_KEY], portsetted),  
                                        (self.__OidDic[SERVER_TRAP_SETTING_ENABLE_BMC_KEY], enableoid),  
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY], trapmode),   
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY], trapversion), 
                                        (self.__OidDic[SERVER_TRAP_SETTING_USER_BMC_KEY], trapuser),                                    
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY], enableAll))                                   
                        else:
                            print "server:%s trap comunity will be set "%ipaddress
                            if 'V2'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion=Integer(2) 
                            if 'V1'==hostdic[CFG_NODE_KEY_CSNMPVERSION].upper():
                                trapversion= Integer(1)
                            trapComunity=OctetString(hostdic[CFG_NODE_KEY_TCNMTY])
                            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(\
                                        useData,
                                        cmdgen.UdpTransportTarget((ipaddress, \
                                                                   hostdic[CFG_NODE_KEY_PPORT])),
                                        (self.__OidDic[SERVER_TRAP_SETTING_IP_BMC_KEY], localaddresssetted), 
                                        (self.__OidDic[SERVER_TRAP_SETTING_PORT_BMC_KEY], portsetted),
                                        (self.__OidDic[SERVER_TRAP_SETTING_ENABLE_BMC_KEY], enableoid),
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPMODE_BMC_KEY], trapmode),
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPVERSION_BMC_KEY], trapversion),
                                        (self.__OidDic[SERVER_TRAP_SETTING_COMMUNITY_BMC_KEY], trapComunity),
                                        (self.__OidDic[SERVER_TRAP_SETTING_TRAPENABLE_BMC_KEY], enableAll))                               
                            if errorIndication is None \
                                    and errorIndex == 6\
                                    and errorStatus == 132:  
                                    print '==========================================================='
                                    print 'set COMMUNITY fail please check your COMMUNITY  config serverIP:%s'%ipaddress
                                    print '==========================================================='
                                    iPlist.append(ipaddress)
                                    continue
                    if errorIndication is None \
                                    and errorIndex == 0 \
                                    and errorStatus == 0:
                            print ' setTrapSendAddress  Done. , %s'%ipaddress
                            print "---------------------------------------------------"                             
                            continue         
                    else: 
                        print "set server trap  port and IP error msg:%s error index %s errorStatus %s ip %s"% \
                            (str( errorIndication ),str(errorIndex) ,str(errorStatus),ipaddress)
                        iPlist.append(ipaddress)      
                        continue                                      
            except Exception, err:
                print 'set trap config exception ;Exceptionstr:'+str(err)
        ret=len(iPlist)           
        return ret,iPlist
    def funReSetServer (self):
        errorIndication = None
        errorStatus = 0
        errorIndex = 0
        varBinds = None
        authProtocol = None
        privProtocol = None
        
        if 'SHA' in self.__parm[CFG_NODE_KEY_CAUTH].upper():
            authProtocol = usmHMACSHAAuthProtocol
        else:
            authProtocol = usmHMACMD5AuthProtocol
        if 'AES' in self.__parm[CFG_NODE_KEY_CPRIV].upper():
            privProtocol = usmAesCfb128Protocol
        else:
            privProtocol = usmDESPrivProtocol
        pwd = self.__parm[CFG_NODE_KEY_CPWD]
        if pwd is None:
            print "need snmp pwd"
            exit() 
        if self.__parm[CFG_NODE_KEY_CUSER] is None: 
            print "need snmp user"
            exit() 
        useData= cmdgen.UsmUserData(self.__parm[CFG_NODE_KEY_CUSER], \
                                                   pwd, \
                                                   pwd, \
                                                   authProtocol, \
                                                   privProtocol)
        serverlist=[]
        if commonFun.matchSigleIp( self.__parm[CFG_NODE_KEY_IP])== True : 
            serverlist.append(self.__parm[CFG_NODE_KEY_IP])
        else:
            _ret,_iPstrlist = commonFun.matchBatchIP(self.__parm[CFG_NODE_KEY_IP])
            if  _ret is not True:  
                print "restet Server error ip is illegal ip:%s"%self.__parm[CFG_NODE_KEY_IP]
                exit()
            serverlist=_iPstrlist
            
        for eachServer in serverlist:
            self._clearTrapIP(eachServer,useData,self.__parm[CFG_NODE_KEY_PPORT])    
        exit()  
    def _clearTrapIP(self ,ipAddr,useData ,iport):
        try: 
            type =None
            type=self._getServerType(ipAddr,useData,iport)                        
            if type is None:       
                print "get server type error ,ip:",ipAddr       
            if "E9000" in type or "E6000" in type:   
                localaddresssetted=IpAddress("" )
                ipoid=self.__OidDic[SERVER_TRAP_SETTING_IP_SMM_KEY]                
            else: 
                localaddresssetted=OctetString("" )
                ipoid=self.__OidDic[SERVER_TRAP_SETTING_IP_BMC_KEY]  
            errorIndication, errorStatus, errorIndex, varBinds = \
                                cmdgen.CommandGenerator().setCmd(\
                                        useData,
                                        cmdgen.UdpTransportTarget((ipAddr,iport)),
                                        (ipoid, localaddresssetted))
            if errorIndication is None \
                                    and errorIndex == 0 \
                                    and errorStatus == 0:
                print ' clear TrapIP Done. , %s'%ipAddr 
                return True
            else : 
                return False            
        except Exception,err:                
            print "clear TrapIP Exception ,err: %s ServerIp:%s"%(err,ipAddr)
            return False        
                  
    def funAdd(self):
        print "addconfig start"
        if commonFun.matchSigleIp( self.__parm[CFG_NODE_KEY_IP])== True :
            #chang parm list to match type witch  saving in __configDiclist
            temKey=self.__parm.pop(CFG_NODE_KEY_IP)
            temDic={}
            _tmpConfigDis={}
            temDic.update(self.__parm )
            _tmpConfigDis= { temKey : temDic }
            self._singleIPHander(_tmpConfigDis)
            self.CofnigServer=True 
        else :
            raise IPExcept  
    def _singleIPHander(self,cofnigDic ):
        _cntConfig = len(self.__configDiclist )
        temKey = cofnigDic.keys()[0] 
        indextoMo=None        
        if _cntConfig >= 1 :
             # ip in config file modify it 
            for i in range( _cntConfig ):
                if temKey in self.__configDiclist[i].keys (): 
                    self.__configDiclist[i][temKey] = cofnigDic[temKey]  
                    indextoMo = i
            #has not ip in configfile just add it         
            if  indextoMo == None:
                self.__configDiclist.append(cofnigDic)             
        # has no items configfils  just add it  
        else: 
            self.__configDiclist.append( cofnigDic ) 
               
    def funBatch(self):
        print "batch config start"
        _ret,_iPstrlist = commonFun.matchBatchIP(self.__parm[CFG_NODE_KEY_IP])
        self.__parm.pop(CFG_NODE_KEY_IP) 
        
        if _ret == True:
            for eachitem in _iPstrlist:
                if self._CheckServiceIsok(eachitem) == True:
                    temDic={}
                    _tmpConfigDis={}
                    temDic.update(self.__parm )
                    _tmpConfigDis={ eachitem : temDic}
                    self._singleIPHander(_tmpConfigDis)
                    self.CofnigServer=True
                else :
                    print  "server ip %s can not connect please check "%eachitem                  
        else:
            raise IPExcept   
    #check service is network and snmp is OK  
    def _getServerType(self,IpStr,usedata,port):
        try:
            errorIndication = None
            errorStatus = 0
            errorIndex = 0
            varBinds = None
            type=None 
            for serverTypeoid in self.__OidDic[SERVER_TYPE_OID_KEY].split(","):  
                errorIndication, errorStatus, errorIndex, varBinds = \
                    cmdgen.CommandGenerator().getCmd(usedata,\
                        cmdgen.UdpTransportTarget((IpStr,port), timeout = 2, retries = 2), serverTypeoid)
                        
                if errorIndication is None \
                    and errorIndex == 0 \
                    and errorStatus == 0: 
                    if (str(varBinds[0][1])==""):
                        continue                    
                    type = varBinds[0][1]
                    break 
        except Exception ,err:
            print "get server type Exception errif:",err         
        finally:                
            return type    
    def _CheckServiceIsok(self,IpStr):
        if 'SHA' in self.__parm[CFG_NODE_KEY_CAUTH].upper():
            authProtocol = usmHMACSHAAuthProtocol
        else:
            authProtocol = usmHMACMD5AuthProtocol
        if 'AES' in self.__parm[CFG_NODE_KEY_CPRIV].upper():
            privProtocol = usmAesCfb128Protocol
        else:
            privProtocol = usmDESPrivProtocol
        pwd = self.__parm[CFG_NODE_KEY_CPWD]
        community =  self.__parm[CFG_NODE_KEY_CCNMTY]
        if self.__parm[CFG_NODE_KEY_CSNMPVERSION].upper() == "V3":
            userDate=cmdgen.UsmUserData(self.__parm[CFG_NODE_KEY_CUSER], \
                                                       pwd, \
                                                       pwd, \
                                                       authProtocol, \
                                                       privProtocol )
        else:
            userDate=cmdgen.CommunityData(community)
        type = self._getServerType(IpStr,userDate,self.__parm[CFG_NODE_KEY_PPORT])
        if type is None:    
            return False
        return True 
        
    def funDel(self):
        print "del config start" 
        try:
            _cntConfig = len(self.__configDiclist )
            #iplist witch should be del
            ipdellist=[]
            #del sigle IP 
            if commonFun.matchSigleIp( self.__parm[CFG_NODE_KEY_IP])== True :
                #chang parm list to match type witch  saving in __configDiclist
                temKey=self.__parm[CFG_NODE_KEY_IP]
                indextoDel=None
                if _cntConfig >= 1 :
                     # find ip if in config file,if yes save it and its config in ipdellist
                    for i in range( _cntConfig ):
                        if temKey in self.__configDiclist[i].keys(): 
                            ipdellist.append(self.__configDiclist[i])
                self._ClearTrapIpBylist(ipdellist)
                self._delIPfromConfig(ipdellist)                
                return 
            #del batch ip 
            _ret,_iPstrlist = commonFun.matchBatchIP(self.__parm[CFG_NODE_KEY_IP])
            if  _ret is True:
                for ip in _iPstrlist :
                    if _cntConfig >= 1 :
                        # find ip if in config file,if yes save it and its config in ipdellist
                        for i in range( _cntConfig ):
                            if ip in self.__configDiclist[i].keys(): 
                                 ipdellist.append(self.__configDiclist[i]) 
                self._ClearTrapIpBylist(ipdellist)
                self._delIPfromConfig(ipdellist)                  
                return 
        except Exception,err:
            print "funDel Exception Errstr:"+str(err)     
        #ip is illegal raise  IPExcept   
        raise IPExcept
        
    def _ClearTrapIpBylist(self,configList):
        try:
            for eachconfig in configList:
                ipAddr=eachconfig.keys()[0]
                confdic=eachconfig.values()[0]
                if 'SHA'.find(str(confdic[CFG_NODE_KEY_CAUTH].upper())) != -1:
                    authProtocol = usmHMACSHAAuthProtocol
                else:
                    authProtocol = usmHMACMD5AuthProtocol
                if 'AES'.find(str(confdic[CFG_NODE_KEY_CPRIV].upper())) != -1:
                    privProtocol = usmAesCfb128Protocol
                else:
                    privProtocol = usmDESPrivProtocol
                useData=cmdgen.UsmUserData(confdic[CFG_NODE_KEY_CUSER], \
                                            confdic[CFG_NODE_KEY_CPWD], \
                                            confdic[CFG_NODE_KEY_CPWD], \
                                            authProtocol, \
                                            privProtocol)
                iport=confdic[CFG_NODE_KEY_PPORT]
                ret=self._clearTrapIP(ipAddr,useData ,iport)
                if ret is False:
                    print "clear server Trap IP fail ,please clear it yourself  server IP :%s "%ipAddr
        except Exception,err:
            print "_ClearTrapIBylist Exception Errstr:"+str(err)      
        
    def _delIPfromConfig(self,configList):
        for ipconfig in configList:
            try: 
                ipaddr =ipconfig.keys()[0]
                _cntConfig = len(self.__configDiclist )
                if _cntConfig < 1:
                    return 
                for i in range( _cntConfig ):   
                    if ipaddr in self.__configDiclist[i].keys(): 
                        del self.__configDiclist[i]
                        break
            except Exception,err:
                print "_delIPfromConfig Exception Errstr:"+str(err)                 
                    
    def funVersion(self):
        print VERSTION_STR
        exit(0) 
    def funInquiry(self):
        print "==============iplist in configfile ====================" 
        for eachitem in self.__configDiclist :
            for eachkey in  eachitem:
                print eachkey  
        exit(0)                
    #creat all config file     
    def creatConfigfile(self):
        print "start CreatConfigfile " 
        self.__creatServerCfg()
        self.__creathostxml() 
    #生成hw_server.cfg 文件
    
    def __gethostservicescontent(self, devicetype, hostname, hostalias, ipaddress):
        _etcPath=self.__getCfgPath()
        # create a blade tmp file for services configuration for current host
        if devicetype == 'Blade':
            commands.getoutput("cat " + _etcPath+ os.path.sep  + "Blade.cfg > /tmp/huaweitmp.cfg")
        # create a rack or HD tmp file for services configuration for current host
        if devicetype != 'Blade' and devicetype != '':
            commands.getoutput("cat " + _etcPath + os.path.sep + "HDorRack.cfg > /tmp/huaweitmp.cfg")
        # update hostname in tmp file
        if hostname:
            commands.getoutput("sed -i 's/hostname/" + hostname + "/g' /tmp/huaweitmp.cfg")
        # update hostalias in tmp file
        if hostalias:
            commands.getoutput("sed -i 's/hostalias/" + hostalias + "/g' /tmp/huaweitmp.cfg")
        # update ipaddress in tmp file
        if ipaddress: 
            commands.getoutput("sed -i 's/ipaddress/" + ipaddress + "/g' /tmp/huaweitmp.cfg")
        # get tmp file content about services for host
        output = commands.getoutput("cat /tmp/huaweitmp.cfg")
        commands.getoutput("rm -rf /tmp/huaweitmp.cfg")
        return output
    
    def __getlistenercontent(self, hostname):
        _etcPath=self.__getCfgPath()
        
        # create a listener tmp file for nagios plugin listener configuration for local host
        commands.getoutput("cat " + _etcPath+ os.path.sep + "listener.cfg > /tmp/listenertmp.cfg")
        # update hostname in tmp file
        commands.getoutput("sed -i 's/localhost/" + hostname + "/g' /tmp/listenertmp.cfg")
        # get content of listener configuration
        output = commands.getoutput("cat /tmp/listenertmp.cfg")
        commands.getoutput("rm -rf /tmp/listenertmp.cfg")
        return output
        
    def __creatServerCfg(self):
        _etcPath=self.__getCfgPath()
        commands.getoutput("rm -rf " +_etcPath + os.path.sep +"hw_server.cfg")
        servicefile=None
        servicefile = open(_etcPath + os.path.sep +"hw_server.cfg",'w')
        for hostdic in self.__configDiclist:
            for hostIpAddress in hostdic.keys():
                _hostParmdic = hostdic[hostIpAddress]
                if _hostParmdic[CFG_NODE_KEY_HOST_NAME] == None:
                    _hostName=hostIpAddress
                else:
                    _hostName =_hostParmdic[CFG_NODE_KEY_HOST_NAME]
                hostalias = _hostName
                if _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'Rack':
                    hostalias = 'RackDetailsStatus@' + _hostName
                elif _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'HighDensity':
                    hostalias = 'HighDensityDetailsStatus@' + _hostName
                elif _hostParmdic[CFG_NODE_KEY_DEVTYPE] == 'Blade':
                    hostalias = 'BladeDetailsStatus@' + _hostName
                cfgcontent = self.__gethostservicescontent(_hostParmdic[CFG_NODE_KEY_DEVTYPE],\
                   _hostName, hostalias, hostIpAddress)
                servicefile.writelines(cfgcontent)
        servicefile.writelines( self.__getlistenercontent("127.0.0.1") )
        servicefile.close()
        commands.getoutput("sudo chown nagios.nagios " + _etcPath + os.path.sep +"hw_server.cfg")
        print "creatServerCfg ok"  
        
    def __getCfgPath(self):
        _etcPath = self._nagiosHomeDir + os.path.sep+"etc"+ os.path.sep+"huawei_server"
        return _etcPath
    
    def __find_nagiosdir(self):
        '''return nagios directory'''
        cmd = "source /etc/profile;echo $NAGIOSHOME"
        procs = commands.getoutput(cmd)
        return procs
    def __getNagiosPath(self):
        return self._nagiosHomeDir   
        
    #creat hua:wei_host.xml:
    def __creathostxml(self):        
        _etcPath=self.__getCfgPath()
        commands.getoutput("rm -rf " +_etcPath + os.path.sep +"huawei_hosts.xml")
        _hostfilePath=_etcPath + os.path.sep + "huawei_hosts.xml"
        try:
            impl = minidom.getDOMImplementation()
            dom = impl.createDocument(None, 'hosts' , None)
            for hostdic in self.__configDiclist:
                for hostIpAddress in hostdic.keys():
                    _hostParmdic = hostdic[hostIpAddress]
                    root = dom.documentElement
                    xhost = dom.createElement( 'host' )
                    root.appendChild(xhost)
                    xdevice = dom.createElement( 'device' )
                    xhost.appendChild(xdevice)
                    xhostname = dom.createElement( 'hostname' )
                    #if hostName =None , hostName = Ip addr          
                    if _hostParmdic[CFG_NODE_KEY_HOST_NAME] == "None":    
                        xhostnamet = dom.createTextNode(None)
                    else : 
                        xhostnamet = dom.createTextNode(hostIpAddress)          
                    xhostname.appendChild(xhostnamet)
                    xdevice.appendChild(xhostname)
                    xipaddress = dom.createElement( 'ipaddress' )
                    xipaddresst = dom.createTextNode(hostIpAddress)
                    xipaddress.appendChild(xipaddresst)
                    xdevice.appendChild(xipaddress)
                    xdevicetype = dom.createElement( 'devicetype' )
                    xdevicetypet = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_DEVTYPE])
                    xdevicetype.appendChild(xdevicetypet)
                    xdevice.appendChild(xdevicetype)
                    xport = dom.createElement( 'port' )
                    xportt = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_PPORT])
                    xport.appendChild(xportt)
                    xdevice.appendChild(xport)
                    # collect info: collectuser/password/authprotocol/privprotocol
                    xcollect = dom.createElement( 'collect' )
                    xhost.appendChild(xcollect)
                    xsnmpversion = dom.createElement( 'snmpversion' )
                    xsnmpversiont = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_CSNMPVERSION])
                    xsnmpversion.appendChild(xsnmpversiont)
                    xcollect.appendChild(xsnmpversion)
                    xuser = dom.createElement( 'user' )
                    xusert = dom.createTextNode(str(_hostParmdic[CFG_NODE_KEY_CUSER]))
                    xuser.appendChild(xusert)
                    xcollect.appendChild(xuser)
                    xpass = dom.createElement( 'pass' )
                    xpasst = dom.createTextNode(self.encrypt(str(_hostParmdic[CFG_NODE_KEY_CPWD])))
                    xpass.appendChild(xpasst)
                    xcollect.appendChild(xpass)
                    xauthprotocol = dom.createElement( 'authprotocol' )
                    xauthprotocolt = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_CAUTH])
                    xauthprotocol.appendChild(xauthprotocolt)
                    xcollect.appendChild(xauthprotocol)
                    xprivprotocol = dom.createElement( 'privprotocol' )
                    xprivprotocolt = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_CPRIV])
                    xprivprotocol.appendChild(xprivprotocolt)
                    xcollect.appendChild(xprivprotocol)
                    xcommunity = dom.createElement( 'community' )
                    xcommunityt = dom.createTextNode(self.encrypt(str(_hostParmdic[CFG_NODE_KEY_CCNMTY])))
                    xcommunity.appendChild(xcommunityt)
                    xcollect.appendChild(xcommunity)
                    # alarm info: trapuser/trapwd/trapauthprotocol/trapprivprotocol
                    xalarm = dom.createElement( 'alarm' )
                    xhost.appendChild(xalarm)
                    xtrapsnmpversion = dom.createElement( 'snmpversion' )
                    xtrapsnmpversiont = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_TSNMPVERSION])
                    xtrapsnmpversion.appendChild(xtrapsnmpversiont)
                    xalarm.appendChild(xtrapsnmpversion)
                    xtrapuser = dom.createElement( 'user' )
                    xtrapusert = dom.createTextNode(str(_hostParmdic[CFG_NODE_KEY_TUSER]))
                    xtrapuser.appendChild(xtrapusert)
                    xalarm.appendChild(xtrapuser)
                    xtrappass = dom.createElement( 'pass' )
                    xtrappasst = dom.createTextNode(self.encrypt(str(_hostParmdic[CFG_NODE_KEY_TPWD])))
                    xtrappass.appendChild(xtrappasst)
                    xalarm.appendChild(xtrappass)
                    xtrapauthprotocol = dom.createElement( 'authprotocol' )
                    xtrapauthprotocolt = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_TAUTH])
                    xtrapauthprotocol.appendChild(xtrapauthprotocolt)
                    xalarm.appendChild(xtrapauthprotocol)
                    xtrapprivprotocol = dom.createElement( 'privprotocol' )
                    xtrapprivprotocolt = dom.createTextNode(_hostParmdic[CFG_NODE_KEY_TPRIV])
                    xtrapprivprotocol.appendChild(xtrapprivprotocolt)
                    xalarm.appendChild(xtrapprivprotocol)
                    xtrapcommunity = dom.createElement( 'community' )
                    xtrapcommunityt = dom.createTextNode(self.encrypt(str(_hostParmdic[CFG_NODE_KEY_TCNMTY])))
                    xtrapcommunity.appendChild(xtrapcommunityt)
                    xalarm.appendChild(xtrapcommunity)
        except Exception, e:  
            print  "parm not right : %s"%e
            sys.exit(1)
             
        xmlfile = open(_hostfilePath , 'w')
        dom.writexml(xmlfile, addindent = '    ' , newl = '\n' , encoding = 'UTF-8')
        xmlfile.close()
        commands.getoutput("sudo chown nagios.nagios " +_etcPath + os.path.sep + "huawei_hosts.xml") 
        print "creathostxml ok" 
     
    #deccode an encrypt funs  -------------
    def dencrypt(self,pkey ):
        return dencryptKey( pkey, self.getrootkey())
    
    def getrootkey(self):
        rootkey = dencryptKey(readKey(),genRootKeyStr())
        return rootkey 
        
    def encrypt(self,pkey):
        encryptpwd = encryptKey(pkey, self.getrootkey())
        return encryptpwd  
    #end deccode an encrypt funs  -------------    
    
     
    def addPlugincfgInNagios(self):
        nagioshome=self.__getNagiosPath()
        NagioscfgFilePath=nagioshome+os.path.sep +"etc"+os.path.sep+"nagios.cfg" 
        strforconfig="cfg_file=%s"%nagioshome+os.path.sep+"etc"+os.path.sep+"huawei_server"+os.path.sep+"hw_server.cfg\n"
        file=None
        try:
            file = open(NagioscfgFilePath,"r+")
            strlist=file.readlines()  
            #had configed so exit             
            if strforconfig in strlist:
                return  
            #cofnig   nagios.cfg  
            file.writelines(strforconfig)   
        except Exception,err:
            print  "addPlugincfgInNagios exception info :" + str(err)  
        finally:
            if file is not None:
                file.close()
    def restartNagios(self):
        print "start kill trapd.py "
        ret = os.system("service nagios stop")
        if not ret == 0:
            print "stop Nagios fail "
        time.sleep(1)  
        trapdpid=commands.getoutput("ps -efww | grep trapd.py | grep -v grep | awk '{print $2}'")
        os.system("kill -9  %s"%trapdpid)
        time.sleep(2)  
        try:
            ret = os.system("service nagios restart")
            if not ret ==0:
                print "start Nagios fail " 
                print "please restart nagios service youself "                  
        except Exception ,err:
            print "start Nagios exception errif : %s"%str(err) 
            print "please restart nagios service yourself "
        print "start Nagios servic ok"
if __name__ == '__main__':
    main() 
       