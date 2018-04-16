#coding=utf-8

'''
' Created on 2013-3-15
' 
' Trap receiver. Catch the trap from agent.
'
'''

from config import VERSTION_STR
from compiler.pycodegen import EXCEPT

NAGIOS_DIR_KEY = 'nagios_dir'
NAGIOS_CMD_FILE_KEY = 'nagios_cmd_file'
LOCAL_ADDRESS_KEY = 'local_address'
LISTEN_PORT_KEY = 'listen_port'
CACHE_PATH_KEY = 'cache_path'
HOST_CHECK_CMD_KEY = 'check_host_cmd'
NAGIOS_CHECK_CMD_KEY = 'check_nagios_cmd'
HOST_CHECK_INTERVAL_KEY = 'check_host_interval'
NAGIOS_CHECK_INTERVAL_KEY = 'check_nagios_interval'

PLUGIN_GENERIC_CFG_KEY = 'GENERIC'
SERVICE_CFG_KEY = 'SERVICEDIC'
TRAP_TIME_FORMAT_KEY = 'trap_time_format'
TRAP_BINDING_VALUES_KEY = 'binding_values_oid'
SERVER_TYPE_OID_KEY = 'server_type_oid'
SERVER_BINDING_EBGUBUD_OID='binding_enginid_oid'
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

TRAP_BINDING_VALUES_FORMAT_KEY = 'binding_values_format'

HOST_CFG_KEY_ISSUCCESS = 'issuccess'
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
HOST_CFG_KEY_MODEL = 'model'
HOST_CFG_KEY_ENGINID = 'enginid'
HOST_TYPE_SMM = 'SMM'
HOST_TYPE_BMC = 'BMC'
HOST_TRAP_SEND_IP_OID_KEY = 'trapsendip'
HOST_TRAP_SEND_PORT_OID_KEY = 'trapsendport'
HOST_TRAP_SEND_ENABLE_OID_KEY = 'trapsendenable'
HOST_TRAP_SEND_USER_OID_KEY = 'trapuseroid'
HOST_TRAP_SEND_VERSION_OID_KEY='trapversionoid'
HOST_TRAP_SEND_TRAPMODE_OID_KEY='trapmodeoid'
HOST_TRAP_SEND_COMMUNITY_OID_KEY='trapcommunityoid'
HOST_TRAP_SEND_ENABLEALL_OID_KEY='trapenablealloid'


SERVERTYPES_SUPPORTED_SEP = ','
HOSTNAME_HOSTTYPE_SEP = ','
EVENTCODE_AND_SENSOR_SEP = ','
EVENTCODE_SENSOR_SEP = '_'
SERVER_TYPE_OID_SEP = ','

import os
import sys
import re
import constInfo
import dataInfo
import time
import thread
import threading
import logging
import logging.handlers as handlers
import ConfigParser
import commands
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACMD5AuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmDESPrivProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmHMACSHAAuthProtocol
from pysnmp.entity.rfc3413.oneliner.cmdgen import usmAesCfb128Protocol 
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

sys.path.append(os.path.dirname(\
                    os.path.dirname(\
                        os.path.normpath(\
                            os.path.join(os.getcwd(), \
                                         os.path.dirname(__file__))))) \
                + os.path.sep \
                + 'libexec' \
                + os.path.sep \
                + 'huawei_server' \
                + os.path.sep \
                + 'eventhandler')

from eventhandler import HandlerFactory
from eventhandler import UnSupportedException
import eventhandler as const


##########################################################################
# 初始化日志记录
##########################################################################
logger = logging.getLogger('huawei_plugin')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(\
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)
filehandler = handlers.TimedRotatingFileHandler(os.path.dirname(__file__) + os.path.sep \
                                                + 'huawei_plugin.log', \
                                                        when='midnight', \
                                                        interval=1, \
                                                        backupCount=30)
filehandler.setLevel(logging.INFO)
errorfilehandler = logging.FileHandler(os.path.dirname(__file__) + os.path.sep \
                                       + 'huawei_plugin_error.log')
errorfilehandler.setLevel(logging.ERROR)
consolehandler.setFormatter(formatter)
filehandler.setFormatter(formatter)
errorfilehandler.setFormatter(formatter)
logger.addHandler(consolehandler)
logger.addHandler(filehandler)
logger.addHandler(errorfilehandler)

class FileExcept(Exception):
    pass

class Initialization(object):
    '''
    ' 初始化，构造配置数据
    ' methods:
    '     start: 开始监听trap
    '''
    def __init__(self):
        logger.info('================================================')
        logger.info('========= %s ======='%VERSTION_STR)
        logger.info('========= Initialization huawei_server_plugin =========')
        logger.info('================================================')
        
        configfilepath = 'etc' + os.path.sep \
                       + 'huawei_server' + os.path.sep \
                       + 'initial.cfg'
        hostfilepath = 'etc' + os.path.sep \
                     + 'huawei_server' + os.path.sep \
                     + 'huawei_hosts.xml'
        pluginfilepath = 'etc' + os.path.sep \
                       + 'huawei_server' + os.path.sep \
                       + 'huawei_plugin.cfg'
        
        try:
            self._snmpcorresponder = SNMPCorresponder()
            self._configdata = ConfigData(self._getFullPath(configfilepath), \
                                          self._getFullPath(hostfilepath), \
                                          self._getFullPath(pluginfilepath), \
                                          self._snmpcorresponder)
        except Exception,err:
            logger.error('init config  excepterr Str:'+str(err))
            sys.exit(-1)
        
        logger.info('Start timer of host checking...')
        self._checkStatusTimer()
        logger.info('checkStatusTimer Done. ')
        logger.info('Start timer of Nagios\'s process checking...')
        self._checkNagiosTimer()
        logger.info('Start timer of Nagios\'s process check Done. ')               
    def start(self):
        '''
        ' 启动接受trap进程
        '''
        TrapReceiver(self._configdata).start()

    def _getFullPath(self, filepath):
        '''
        ' 获取配置文件的完整路径
        ' params:
        '     filepath: 相对路径
        ' return str: 完整路径名
        '''
        curpath = os.path.normpath(os.path.join(os.getcwd(), \
                                                os.path.dirname(__file__)))
        return os.path.dirname(os.path.dirname(curpath)) \
             + os.path.sep \
             + filepath
    def __find_ckmkVersion(self):
        '''return nagios directory'''
        cmd = "source /etc/profile;echo $NAGIOS_CHECKMK_VERSION"
        procs = commands.getoutput(cmd)
        return procs 
    def  getSiteUsrInfo(self):
        usrFile=self._configdata.Nagiosdir+os.path.sep+"etc/huawei_server/usrFile.cfg"
        strlist =[]
        usr ='prod' 
        group ='prod'
        file=None 
        try:
            file = open(usrFile,"r+")
            strlist=file.readlines()  
        except Exception, e :
            print 'error : open usrFile.cfg error :  '+str(e)
        finally:
            if not file  is None:
                file.close()
        if (strlist ==[] or strlist==None):
            return usr ,group      
        for eachline in strlist:
            if re.findall(r'.*usr.*=.*', eachline):
                usr = eachline.split('=')[1]
            if re.findall(r'.*group.*=.*', eachline):  
                group =eachline.split('=')[1]   
        return usr.strip(),group.strip() 

    def _checkNagiosTimer(self):
        '''
        ' 检查Nagios主程序是否启动
        '''
        
        NagiosbinPath=''
        if '1_4' in self.__find_ckmkVersion() or   '1_5' in self.__find_ckmkVersion() :
            usr,group = self.getSiteUsrInfo()
            NagiosbinPath = "/omd/sites/%s/bin/nagios"%usr
        else :
            NagiosbinPath = self._configdata.Nagiosdir \
                              + os.path.sep \
                              + 'bin' \
                              + os.path.sep \
                              + 'nagios'

        retVal = os.system(self._configdata.NagiosCheckCmd\
                           % NagiosbinPath)
        if retVal != 0:
            thread.interrupt_main()
        nagiostimer = threading.Timer(self._configdata.NagiosCheckInterval, \
                                      self._checkNagiosTimer)
        nagiostimer.setDaemon(True)
        nagiostimer.start()



    def _checkStatusTimer(self):
            '''
            ' 检查当前状态，包括主机是否可达，告警缓存文件是否处理
            '''
            cmdfile = None
            logger.info("timer begin .")
            try:
                warningfiles = os.listdir(self._configdata.Cachepath)
                nagioscmdtemplate = const.NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT \
                          + '%s' \
                          + const.NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT + ' ' \
                          + const.NAGIOS_CMD_SIGN + const.NAGIOS_CMD_SEP \
                          + '%s' + const.NAGIOS_CMD_SEP \
                          + '%s' + const.NAGIOS_CMD_SEP \
                          + '%s' + const.NAGIOS_CMD_SEP \
                          + '%s' \
                          + '\n'
                                   
                #删除已移除设备的告警文件          
                for filename in warningfiles:
                    hostIp = filename[:filename.find('_')]
                    isContain = False
                    for agentip, hostdic in self._configdata.Hostdata.items():
                        if hostIp == agentip:
                           isContain = True
                    if isContain == False:
                        os.remove(self._configdata.Cachepath + os.path.sep + filename)
                        logger.info("delete non-host alarm infor success!") 
                #开始检查告警文件         
                logger.info("time begin to check warngingfiles:")
                for agentip, hostdic in self._configdata.Hostdata.items():
                    # 当HOST_CFG_KEY_MODEL为None，标识无法获取设备型号
                    # 当HOST_CFG_KEY_ISSUCCESS为False，标识无法设置设备trap信息
                    self._configdata._addType2HostCfgWithSNMP(hostdic)
                    if hostdic[HOST_CFG_KEY_MODEL] is None \
                            or hostdic[HOST_CFG_KEY_ISSUCCESS] == False:
                        logger.info("type of "+ str(agentip) + " is null or failure of trap ip !")
                        for srvname in ['alarm']:
                            nagioscmd = nagioscmdtemplate % \
                                    (str(time.time()), hostdic[HOST_CFG_KEY_NAME], \
                                     srvname, str(const.STATUS_UNKNOWN_INT), \
                                     const.STATUS_UNKNOWN_STR)
                            cmdfile = open(self._configdata.Cmdfilepath, 'a')
                            cmdfile.write(nagioscmd)
                            logger.info(" nagioscmd in writting to cmdfile in timer is "+ str(nagioscmd))
                        self._configdata.Hostdata.pop(agentip, None)
                        continue
                    hostname = hostdic[HOST_CFG_KEY_NAME]
                    hostStatus = self._checkHosts(agentip)
                    logger.info("host status of " + str(agentip) + " is " + str(hostStatus))
                    if hostStatus[0] == const.STATUS_OK_INT:
                        if warningfiles is None or len(warningfiles) < 1:
                                srvname ='alarm'
                                nagioscmd = nagioscmdtemplate % \
                                        (str(time.time()), hostname, \
                                         srvname, str(const.STATUS_OK_INT), \
                                         const.STATUS_OK_STR)
                                cmdfile = open(self._configdata.Cmdfilepath, 'a')
                                cmdfile.write(nagioscmd)
                                logger.info(" nagioscmd in writting to cmdfile in timer is "+ str(nagioscmd))
                        else:
                            statusDic = self._checkWarningCacheFiles(agentip, warningfiles)
                            for srvname, status in statusDic.items():
                                nagioscmd = nagioscmdtemplate % \
                                    (status[2], hostname, \
                                     srvname, str(status[0]), \
                                     status[1])
                                cmdfile = open(self._configdata.Cmdfilepath, 'a')
                                cmdfile.write(nagioscmd)
                                logger.info(" nagioscmd in writting to cmdfile in timer is "+ str(nagioscmd))
                    else:
                            srvname ='alarm' 
                            nagioscmd = nagioscmdtemplate % \
                                    (str(time.time()), hostname, \
                                     srvname, str(const.STATUS_UNKNOWN_INT), \
                                     const.STATUS_UNKNOWN_STR)
                            cmdfile = open(self._configdata.Cmdfilepath, 'a')
                            cmdfile.write(nagioscmd)
                            logger.info(" nagioscmd in writting to cmdfile in timer is "+ str(nagioscmd))
            except Exception, err:
                logger.error("timer of checkWarningfiles exists error, infor: "+str(err))
                if not cmdfile is None:
                    cmdfile.close()
            else:
                if not cmdfile is None:
                    cmdfile.close()
            checker = threading.Timer(self._configdata.HostCheckInterval, \
                                      self._checkStatusTimer)
            checker.setDaemon(True)
            checker.start()
            logger.info("timer of checkwaringfiles  started.")

    def _checkHosts(self, agentip):
        '''
        ' 检查主机可达
        ' params:
        '     agentip: 受管服务器IP
        ' return:
        '     tuple: 主机可达状态
        '''
        retVal = os.system(self._configdata.HostCheckCmd % agentip)
        if retVal == 0:
            return (const.STATUS_OK_INT, const.STATUS_OK_STR)
        else:
            return (const.STATUS_UNKNOWN_INT, const.STATUS_UNKNOWN_STR)

    def _checkWarningCacheFiles(self, hostip, warningfiles):
        '''
        ' 检查告警缓存文件
        ' params:
        '     hostip: 受管主机IP
        '     warningfiles: 告警缓存文件
        ' return:
        '     dic: 指定主机的各监控服务状态
        '''
        cachefile = None
        try:
            statusDic = {}
            statuslst = []
            info = ''
            temp = 0
            srvname ='alarm'
            warnList=[]
            for filename in warningfiles:
                filenameseq = filename.split(const.CMD_FILE_NAME_SEP)
                if len(filenameseq) < 4:
                     continue
                agentip = filenameseq[0]
                eventcode = filenameseq[1]
                sensor = filenameseq[2]
                WarnId=eventcode+sensor
                #do not display same warning 
                if WarnId in warnList:
                    continue
                warnList.append(WarnId)
                if len(filenameseq)> 4:
                    timestamp = filenameseq[4]
                else:
                    timestamp = filenameseq[3]
                if agentip == hostip:
                    cachefile = open(
                                self._configdata.Cachepath + os.path.sep + filename, \
                                'r')
                    fileline = cachefile.readline()
                    statuslst.append(int(fileline.split(\
                                                const.CMD_FILE_CONTENT_SEP)[0]))
                    temp += 1
                    info = info + str(temp) + "."\
                                 + fileline.split(const.CMD_FILE_CONTENT_SEP)[1] \
                                 + ';  '
                    cachefile.close()
                if len(statuslst) < 1:
                    statusDic[srvname] = \
                            (const.STATUS_OK_INT, const.STATUS_OK_STR, timestamp)
                else:
                    statuslst.sort(reverse=True)
                    statusDic[srvname] = (statuslst[0], info, timestamp)
            return statusDic
        except Exception, err:
            logger.error( "_checkWarningCacheFiles exception "+str(err))
            if not cachefile is None:
                cachefile.close()
        else:
            if not cachefile is None:
                cachefile.close()


class TrapReceiver(object):
    '''
    ' 接受Trap数据，构造trap数据对象并调用相应处理
    ' methods:
    '     start: 启动监听进程
    '''
    def __init__(self, configdata):
        self._configdata = configdata

    def start(self):
        '''
        ' 启动监听进程
        ' raise Exception: 异常停止时抛出
        '''
        logger.info('Start trap listener...')
        # Create SNMP engine with autogenernated engineID and pre-bound
        # to socket transport dispatcher
        snmpEngine = engine.SnmpEngine()
        
        # Transport setup
        # UDP over IPv4
        config.addSocketTransport(
            snmpEngine,
            udp.domainName,
            udp.UdpTransport().openServerMode((self._configdata.Localaddress, \
                                             self._configdata.Listenport))
        )
        
        try:
            for agentip in self._configdata.Hostdata.keys():
                issuccess = self._configdata.Hostdata[agentip][HOST_CFG_KEY_ISSUCCESS]
                if issuccess != True:
                    continue 
                version = self._configdata.Hostdata[agentip][HOST_CFG_KEY_TRAPSNMPVERSION]
                if 'V3' == version.upper():
                     # SNMPv3/USM setup
                    authProtocol = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_AUTHPROTOCOL])
                    privProtocol = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_PRIVPROTOCOL])
                    username = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_USER])
                    password = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_PASS])
                    enginid = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_ENGINID])
                   
                    if enginid is None or enginid == '':
                        logger.info("enginid is null,please check device,ipaddr :" + str(agentip))
                        strEnginid=None
                    else :
                        strEnginid=v2c.OctetString(hexValue=enginid)
                        
                    if authProtocol =='MD5' and privProtocol == "DES":
                        config.addV3User(
                            snmpEngine, username,
                            config.usmHMACMD5AuthProtocol, password,
                            config.usmDESPrivProtocol, password,
                            contextEngineId=strEnginid
                        )
                    elif authProtocol =='MD5' and privProtocol == "AES":
                         config.addV3User(
                            snmpEngine, username,
                            config.usmHMACMD5AuthProtocol, password,
                            config.usmAesCfb128Protocol, password,
                            contextEngineId=strEnginid
                        ) 
                    elif authProtocol =='SHA' and privProtocol == "DES":
                         config.addV3User(
                            snmpEngine, username,
                            config.usmHMACSHAAuthProtocol, password,
                            config.usmDESPrivProtocol, password,
                            contextEngineId=strEnginid
                        )
                    elif authProtocol =='SHA' and privProtocol == "AES":
                         config.addV3User(
                            snmpEngine, username,
                            config.usmHMACSHAAuthProtocol, password,
                            config.usmAesCfb128Protocol, password,
                            contextEngineId=strEnginid
                        )       
                else:
                    # v1/2 setup
                    trapcommunity = str(self._configdata.Hostdata[agentip][HOST_CFG_KEY_TRAPCOMMUNITY])
                    config.addV1System(snmpEngine, 'test-agent', trapcommunity)
        except Exception, err:
            logger.error("cache userinfor ,error :" +str(err))
            snmpEngine.transportDispatcher.closeDispatcher()
            raise   
           
        # Register SNMP Application at the SNMP engine
        # Run I/O dispatcher which would receive queries and send confirmations
        try:
            
            ntfrcv.NotificationReceiver(snmpEngine, self._cbHandler)
            # this job would never finish
            snmpEngine.transportDispatcher.jobStarted(1) 
            logger.info('Plugin working now...')
            snmpEngine.transportDispatcher.runDispatcher()
            logger.info("transportDispatcher start successfully.")
            
        except Exception, err:
            logger.error("transportDispatcher close,error :" +str(err))
            snmpEngine.transportDispatcher.closeDispatcher()
            raise
        
      # Callback function for receiving notifications
    def _cbHandler(self, snmpEngine, stateReference, contextEngineId, contextName,
                varBinds, cbCtx):
        try:
            agentip = snmpEngine.msgAndPduDsp.getTransportInfo(stateReference)[1][0]
            # 构造处理器处理trap消息
            handler = HandlerFactory.createHandler(agentip, varBinds, \
                                                       self._configdata)
            handler.handle()
        except Exception,err:
            logger.error("HandlerFactory err :" + str(err))


class ConfigData(object):
    '''
    ' 配置数据
    ' methods:
    '     getHostName: 根据配置文件，读Agent IP对应的用户定义的主机名称信息
    '     getHostType: 根据配置文件，读Agent IP对应的用户定义的主机型号信息
    '     getTimeFormat: 获取trap中告警时间格式
    '     getBindingValuesOID: 获取Trap绑定值的固定OID号
    '     getBindingValuesFormat: 获取解析绑定值的正则式
    '     getSupportedServerTypes: 获取支持的服务器型号列表
    '     getServiceCfgDic: 获取监控服务配置信息字典
    ' properties:
    '     Nagiosdir: Nagios安装主目录
    '     Cmdfilepath: Nagios外部命令文件地址
    '     Localaddress: 本地监听IP
    '     Listenport: 监听端口号
    '     Cachepath: 告警缓存文件目录路径
    '     HostCheckCmd: 主机检查命令
    '     NagiosCheckCmd: Nagios主程序检查命令
    '     Hostdata: 主机IP, 名称, 型号关系字典
    '     Hostmodelinfodic: 服务器型号相关数据
    '''
    def __init__(self, configfilepath, hostfilepath, \
                    pluginfilepath, snmpcorresponder):
        try:
            self._snmpcorresponder = snmpcorresponder
            self._checkPathNotEmpty(configfilepath, hostfilepath, pluginfilepath)
            self._nagiosdir = ''
            self._cmdfilepath = ''
            self._localaddress = ''
            self._listenport = -1
            self._cachepath = ''
            self._hostcheckcmd = ''
            self._hostcheckinterval = -1.0
            self._nagioscheckcmd = ''
            self._nagioscheckinterval = -1.0
            self._parseInitFile(configfilepath)
            self._hostmodelinfodic = {}
            self._parsePluginFile(pluginfilepath)
            self._hostdata = {}
            self._parseHostFile(hostfilepath)
            self._checkHostFileConfig()
            self._checkPluginConfig()
         
        except ConfigException, err:
            logger.error(str(err))
            raise
        except Exception, err:
            logger.error('Unknown error. Cause: \n' + str(err))
            raise


    def getHostName(self, agentip):
        '''
        ' 根据配置文件，读取Agent IP对应的用户定义的主机名称
        ' params:
        '     agentip: 发送trap的主机IP
        ' return 获取agent ip指定的主机名称
        '''
        return self._hostdata.get(agentip).get('name')

    def getHostType(self, agentip):
        '''
        ' 根据配置文件，读Agent IP对应的用户定义的主机型号
        ' params:
        '     agentip: 发送trap的主机IP
        ' return str: 获取agent ip指定的主机型号
        '''
        return self._hostdata.get(agentip).get(HOST_CFG_KEY_MODEL)

    def getTimeFormat(self):
        '''
        ' 获取trap中告警时间格式
        ' return str: trap中告警的时间格式
        '''
        return self._hostmodelinfodic[TRAP_TIME_FORMAT_KEY]

    def getBindingValuesOID(self):
        '''
        ' 获取Trap绑定值的固定OID号
        ' return str: 绑定值的固定OID
        '''
        return self._hostmodelinfodic[TRAP_BINDING_VALUES_KEY]

    def getBindingValuesFormat(self):
        '''
        ' 获取解析绑定值的正则式
        ' return str: 获取绑定值的正则式
        '''
        return self._hostmodelinfodic[TRAP_BINDING_VALUES_FORMAT_KEY]
		
    def _parseInitFile(self, configfilepath):
        '''
        ' 解析初始化配置文件
        ' params:
        '     configfilepath: 初始化配置文件路径
        ' raise ConfigException: 读写文件或解析错误时抛出
        '''
        logger.info('Parse init config file...')
        parser = ConfigParser.ConfigParser()
        configdata = {}
        try:
            file = open(configfilepath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    configdata[key] = value
            self.Nagiosdir = configdata.get(NAGIOS_DIR_KEY)
            self.Cmdfilepath = configdata.get(NAGIOS_CMD_FILE_KEY)
            self.Localaddress = configdata.get(LOCAL_ADDRESS_KEY)
            self.Listenport = int(configdata.get(LISTEN_PORT_KEY))
            self.Cachepath = configdata.get(CACHE_PATH_KEY)
            self.HostCheckCmd = configdata.get(HOST_CHECK_CMD_KEY)
            self.HostCheckInterval = float(configdata.get(HOST_CHECK_INTERVAL_KEY))
            self.NagiosCheckCmd = configdata.get(NAGIOS_CHECK_CMD_KEY)
            self.NagiosCheckInterval = float(configdata.get(NAGIOS_CHECK_INTERVAL_KEY))
            logger.info('Parse init config file complete. ')
        except IOError, err:
            file.close()
            raise ConfigException('Open initial file error. ' + '\n' + str(err))
        except ConfigException, err:
            file.close()
            raise
        except Exception, err:
            file.close()
            raise ConfigException('Initial file invalid. ' + '\n' + str(err))
        else:
            file.close()
            

    def _parseHostFile(self, hostfilepath):
        '''
        ' 解析主机定义文件
        ' params:
        '     hostfilepath: 主机定义文件路径
        ' raise ConfigException: 文件读写错误或解析错误时抛出
        '''
        logger.info('Parse host config file...')
        try:
            file = open(hostfilepath, 'r')
            doc = minidom.parseString(file.read())    
            hostdic = None
            for hostnode in doc.documentElement.getElementsByTagName(HOST_CFG_KEY_HOST):
                hostdic = {}
                for node in hostnode.childNodes:
                      if  node.nodeName==HOST_CFG_KEY_DEVICE:
                          hostdic[HOST_CFG_KEY_NAME] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_HOSTNAME)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                          hostdic[HOST_CFG_KEY_IP] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_IP)[0]\
                                  .childNodes[0] \
                                  .nodeValue.strip())
                          hostdic[HOST_CFG_KEY_DEVICETYPE] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_DEVICETYPE)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                          hostdic[HOST_CFG_KEY_PORT] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_PORT)[0]\
                                   .childNodes[0] \
                                   .nodeValue.strip())
                      elif  node.nodeName==HOST_CFG_KEY_ALARM:
                          hostdic[HOST_CFG_KEY_USER] = \
                                   str(node.getElementsByTagName(HOST_CFG_KEY_USER)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip())
                          hostdic[HOST_CFG_KEY_PASS] = \
                                   self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_PASS)[0]\
                                   .childNodes[0]\
                                   .nodeValue.strip()))
                          hostdic[HOST_CFG_KEY_TRAPSNMPVERSION] = \
                                    str(node.getElementsByTagName(HOST_CFG_KEY_TRAPSNMPVERSION)[0]\
                                    .childNodes[0]\
                                    .nodeValue.strip())
                          hostdic[HOST_CFG_KEY_TRAPCOMMUNITY] = \
                                     self.dencrypt(str(node.getElementsByTagName(HOST_CFG_KEY_TRAPCOMMUNITY)[0]\
                                     .childNodes[0]\
                                     .nodeValue.strip()))
                          if node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL).length != 0:
                               hostdic[HOST_CFG_KEY_AUTHPROTOCOL] = \
                                           str(node.getElementsByTagName(HOST_CFG_KEY_AUTHPROTOCOL)[0]\
                                           .childNodes[0] \
                                           .nodeValue.strip())
                          else:
                                hostdic[HOST_CFG_KEY_AUTHPROTOCOL] = "SHA"
                          if node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL).length != 0:
                                hostdic[HOST_CFG_KEY_PRIVPROTOCOL] = \
                                            str(node.getElementsByTagName(HOST_CFG_KEY_PRIVPROTOCOL)[0]\
                                            .childNodes[0] \
                                            .nodeValue.strip())
                          else:
                                hostdic[HOST_CFG_KEY_PRIVPROTOCOL] = "AES" 
                                 
                      else:
                           continue
                self._addType2HostCfgWithSNMP(hostdic)
        except IOError, err:
            file.close()
            raise ConfigException('Open host config file error. \n' + str(err))
        except ConfigException, err:
            file.close()
            raise ConfigException('host config file error. \n' + str(err))
        except Exception, err:
            file.close()
            raise ConfigException('Host config file invalid. \n' + str(err))
        else:
            file.close()

    def _addType2HostCfgWithSNMP(self, hostdic):
        '''
        ' 使用SNMP协议获取主机型号
        ' params:
        '     hostdic: 主机信息字典
        '''
        ipaddress = hostdic[HOST_CFG_KEY_IP]
        type = None
        generaltype = None
        enginid =None
        try:
            for typeoid in self._hostmodelinfodic[SERVER_TYPE_OID_KEY].split(','):
                type = self._snmpcorresponder.getHostType(hostdic, typeoid)
                if not type is None:
                    break
            if type is None:
                logger.error('Could not get type of host: ' + ipaddress)
            else:
                generaltype = type
            endinidoid = self._hostmodelinfodic[SERVER_BINDING_EBGUBUD_OID]
            enginid = self._snmpcorresponder.getHostType(hostdic, endinidoid,'enginid')
        except Exception,err:
            logger.error("getting type of host error,please check device. IP=%s, error info=%s"%(ipaddress+ str(err) ))
            
        if generaltype is None:
            hostdic[HOST_CFG_KEY_TYPE] = None
        elif 'E9000' in generaltype or 'E6000' in generaltype:
            hostdic[HOST_CFG_KEY_TYPE] = HOST_TYPE_SMM       
        else:
            hostdic[HOST_CFG_KEY_TYPE] = HOST_TYPE_BMC
        if generaltype is None:
            hostdic[HOST_CFG_KEY_MODEL] = generaltype
        else:
            hostdic[HOST_CFG_KEY_MODEL] = generaltype
        hostdic[HOST_CFG_KEY_ENGINID]=enginid    
        hostdic[HOST_CFG_KEY_ISSUCCESS] = True
        self._hostdata[ipaddress] = hostdic
    
    def readKey(self):
        try:
            file=None        
            kfilepath = self._nagiosdir + '/etc' + os.path.sep \
                           + 'huawei_server' + os.path.sep \
                           + 'configInfo.cfg'
            file = open(kfilepath, 'r')
            key = file.readline()
    
        except IOError, err:
            raise FileExcept('Write warning file error. Cause: \n' \
                                  + str(err))
            if file is not None:                      
                file.close()
        except Exception, err:
            raise FileExcept(\
                        'Unknown error when read key file. Cause: \n' \
                        + str(err))
            if file is not None:                      
                file.close()
        else:
            if file is not None:                      
                file.close()
        if key is not None :
            return key
        else:
            return constInfo.DATA_CONS
    
    def genRootKeyStr(self):
        configfilepath = self._nagiosdir + '/etc' + os.path.sep \
                           + 'huawei_server' + os.path.sep \
                           + 'initial.cfg'
        parser = ConfigParser.ConfigParser()
        configdata = {}
        rootkey = ""
        file=None
        try:
            file = open(configfilepath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    configdata[key] = value
            rootkey = configdata.get("nagios_costant3")
            
    
        except IOError, err:
            if file is not None:                      
                file.close()
            raise FileExcept('Open initial file error. ' + '\n' + str(err))
        except FileExcept, err:
            if file is not None:                      
                file.close()
            raise
        except Exception, err:
            if file is not None:                      
                file.close()
            raise FileExcept('Initial file invalid. ' + '\n' + str(err))
        else:
            if file is not None:                      
                file.close()
    
        if rootkey is not None :
            key = dataInfo.CONSTANT1 + rootkey + constInfo.CONSTANT2
            return key
        else:
            return ""   
    def dencryptKey(self,pkey, rootkey):
        
        if rootkey is not None:
            encryptStr = os.popen("echo " +  "'" + pkey + "'" +  " | openssl aes-256-cbc -d -k " +  "'" + rootkey + "'" +  " -base64")\
                                            .read().strip()
        return encryptStr       
    
    
    def dencrypt(self,str):
        '''
        ' aes解密，依赖linux平外，依赖openssl
        '''
        key = self.readKey()
        rootKey = self.genRootKeyStr()
         
        k = self.dencryptKey(key, rootKey)
         
        dencryptStr = os.popen("echo " +  "'" + str + "'" +  " | openssl aes-256-cbc -d -k " + "'" +  k +  "'" + " -base64")\
                                .read().strip()
                       
        if dencryptStr is None or dencryptStr == '':
            return ''
        if dencryptStr == str:
            return ''
        return dencryptStr
    
    def _parsePluginFile(self, pluginfilepath):
        '''
        ' 解析插件配置文件
        ' params:
        '     pluginfilepath: 插件配置文件路径
        ' raise ConfigException: 当文件读写错误或解析失败时抛出
        '''
        logger.info('Parse plugin config file...')
        parser = ConfigParser.ConfigParser()
        file=None
        try:
            file = open(pluginfilepath, 'r')
            parser.readfp(file)
            for section in parser.sections():
                datadic = {}
                if section == PLUGIN_GENERIC_CFG_KEY:
                    for (key, value) in parser.items(section):
                        self._hostmodelinfodic[key] = value
                else:
                    for (key, value) in parser.items(section):
                        self._hostmodelinfodic[section][key] = value     
            logger.info('Parse plugin config file complete. ')
        except IOError, err:
            if file is not None:                      
                file.close()
            raise ConfigException('Open plugin config file error. ' \
                                + '\n' \
                                + str(err))
        except ConfigException:
            if file is not None:                      
                file.close()
            raise
        except Exception, err:
            if file is not None:                      
                file.close()
            raise ConfigException('Plugin config file invalid. ' \
                                + '\n' \
                                + str(err))
        else:
            if file is not None:                      
                file.close()
            file.close()

    def _checkPathNotEmpty(self, configfilepath, hostfilepath, pluginfilepath):
        '''
        ' 检查所有路径不为空
        ' params:
        '     configfilepath: 初始化文件路径
        '     hostfilepath: 主机定义文件路径
        '     pluginfilepath: 插件配置文件路径
        ' raise ConfigException: 当有任何一个配置文件路径为空时抛出
        '''
        if configfilepath is None or configfilepath == '':
            raise ConfigException('The path of init file is empty. ')
        if hostfilepath is None or hostfilepath == '':
            raise ConfigException('The path of host file is empty. ')
        if pluginfilepath is None or pluginfilepath == '':
            raise ConfigException('The path of plugin file is empty. ')

    def _checkHostFileConfig(self):
        '''
        ' 检查主机配置, 至少要有一个华为主机配置，才能启动
        ' raise ConfigException: 当配置不合法或无配置时抛出
        '''
        if len(self._hostdata) == 0:
            raise ConfigException(\
                                'Must configure one host of huawei at least. ')
        for key in self._hostdata.keys():
            if re.match(const.IP_ADDRESS_FORMAT, key) is None:
                raise ConfigException(\
                                'The ip address of host of huawei must valid. ')
            if self.getHostType(key) is None:
                continue
           
                

    def _checkPluginConfig(self):
        '''
        ' 检查插件配置
        ' raise ConfigException: 当时间格式不对或OID不存在, 
        '                        或服务名与事件码对应关系不存在等错误配置时抛出
        '''
        if self.getTimeFormat() is None or self.getTimeFormat() == '':
            raise ConfigException('Plugin config error. No time format. ')
        if self.getBindingValuesOID() is None \
                                        or self.getBindingValuesOID() == '':
            raise ConfigException(\
                    'Plugin config error. No binding values OID. ')
        if self.getBindingValuesFormat() is None \
                                    or self.getBindingValuesFormat() == '':
            raise ConfigException(\
                    'Plugin config error. No binding values format. ')

    def getNagiosdir(self):
        '''
        ' 获取Nagios主目录
        ' return str: Nagios主目录地址
        '''
        return self._nagiosdir

    def setNagiosdir(self, nagiosdir):
        '''
        ' 设置Nagios主目录
        ' params:
        '     nagiosdir: nagios主目录地址
        ' raise ConfigException: 目录地址为空时抛出
        '''
        if nagiosdir is None or not os.path.exists(nagiosdir):
            raise ConfigException('"nagios_dir" must be exists. ')
        self._nagiosdir = nagiosdir

    def getCmdfilepath(self):
        '''
        ' 获取Nagios外部命令文件路径
        ' return str: Nagios外部命令文件路径
        '''
        return self._cmdfilepath

    def setCmdfilepath(self, cmdfilepath):
        '''
        ' 设置Nagios外部命令文件路径
        ' params:
        '     cmdfilepath: Nagios外部命令文件路径
        ' raise ConfigException: 路径为空时抛出
        '''
        if cmdfilepath is None or not os.path.exists(cmdfilepath):
            raise ConfigException('"nagios_cmd_file" must be exists. ')
        self._cmdfilepath = cmdfilepath

    def getLocaladdress(self):
        '''
        ' 获取本地IP地址
        ' return str: 本地IP地址
        '''
        return self._localaddress

    def setLocaladdress(self, localaddress):
        '''
        ' 设置本地IP地址
        ' params:
        '     localaddress: 本地IP地址
        ' raise ConfigException: IP地址为空或不合法时抛出
        '''
        if localaddress is None \
                    or re.match(const.IP_ADDRESS_FORMAT, localaddress) is None:
            raise ConfigException(\
                            '"local_address" is required and must be valid. ')
        self._localaddress = localaddress

    def getListenport(self):
        '''
        ' 获取监听端口
        ' return int: 监听端口
        '''
        return self._listenport

    def setListenport(self, listenport):
        '''
        ' 设置监听端口
        ' params:
        '     listenport: 监听端口, 必须为1024-65535
        ' raise ConfigException: 不是数据或超出范围时抛出
        '''
        try:
            int(listenport)
        except ValueError:
            raise ConfigException('"listen_port must be a number. "')

        if listenport is None or listenport <= 1024 or listenport >= 65535:
            raise ConfigException(\
                            '"listen_port" is required and must be valid. ')
        self._listenport = listenport

    def getCachepath(self):
        '''
        ' 获取缓存文件目录
        ' return str: 缓存文件目录路径
        '''
        return self._cachepath

    def setCachepath(self, cachepath):
        '''
        ' 设置缓存文件路径
        ' params:
        '     cachepath: 缓存文件路径
        ' raise ConfigException: 缓存文件路径不存在时抛出
        '''
        if cachepath is None or not os.path.exists(cachepath):
            raise ConfigException('"cache_path" must be exists. ')
        self._cachepath = cachepath

    def getHostdata(self):
        '''
        ' 获取主机配置数据
        ' return dic: 主机相关信息字典
        '''
        return self._hostdata

    def getHostmodelinfodic(self):
        '''
        ' 获取主机型号信息
        ' return dic: 与主机型号配置相关的数据字典
        '''
        return self._hostmodelinfodic

    def getHostCheckCmd(self):
        '''
        ' 获取主机检查命令
        ' return str: 主机检查命令
        '''
        return self._hostcheckcmd

    def setHostCheckCmd(self, hostcheckcmd):
        '''
        ' 设置主机检查命令
        ' params:
        '     hostcheckcmd: 主机检查命令
        '''
        self._hostcheckcmd = hostcheckcmd

    def getHostCheckInterval(self):
        '''
        ' 获取主机检查频率
        ' return float: 主机检查频率
        '''
        return self._hostcheckinterval

    def setHostCheckInterval(self, hostcheckinterval):
        '''
        ' 设置主机检查频率
        ' params:
        '     hostcheckinterval: 主机检查频率
        '''
        self._hostcheckinterval = hostcheckinterval

    def getNagiosCheckCmd(self):
        '''
        ' 获取Nagios主程序检查命令
        ' return str: Nagios主程序检查命令
        '''
        return self._nagioscheckcmd

    def setNagiosCheckCmd(self, nagioscheckcmd):
        '''
        ' 设置Nagios主程序检查命令
        ' params:
        '     nagioscheckcmd: Nagios主程序检查命令
        '''
        self._nagioscheckcmd = nagioscheckcmd

    def getNagiosCheckInterval(self):
        '''
        ' 获取Nagios主程序检查频率
        ' return float: Nagios主程序检查频率
        '''
        return self._nagioscheckinterval

    def setNagiosCheckInterval(self, nagioscheckinterval):
        '''
        ' 设置Nagios主程序检查频率
        ' params:
        '     nagioscheckinterval: Nagios主程序检查频率
        '''
        self._nagioscheckinterval = nagioscheckinterval

    Nagiosdir = property(fget=getNagiosdir, fset=setNagiosdir)
    Cmdfilepath = property(fget=getCmdfilepath, fset=setCmdfilepath)
    Localaddress = property(fget=getLocaladdress, fset=setLocaladdress)
    Listenport = property(fget=getListenport, fset=setListenport)
    Cachepath = property(fget=getCachepath, fset=setCachepath)
    HostCheckInterval = property(fget=getHostCheckInterval, fset=setHostCheckInterval)
    HostCheckCmd = property(fget=getHostCheckCmd, fset=setHostCheckCmd)
    NagiosCheckInterval = property(fget=getNagiosCheckInterval, fset=setNagiosCheckInterval)
    NagiosCheckCmd = property(fget=getNagiosCheckCmd, fset=setNagiosCheckCmd)
    Hostdata = property(fget=getHostdata)
    Hostmodelinfodic = property(fget=getHostmodelinfodic)


class SNMPCorresponder(object):
    '''
    ' SNMP通信器
    '''
    def __init__(self):
        pass

    def getHostType(self, hostdic, typeoid, param=None):
        '''
        ' 获取指定主机的型号名称
        ' params:
        '     hostdic: 要获取型号的主机信息字典
        '     typeoid: 主机型号存储的MIB库节点
        ' return str: 主机型号名称
        ' raise ConfigException: 当获取不到主机型号时抛出
        '''
        errorIndication = None
        errorStatus = 0
        errorIndex = 0
        varBinds = None
        ipaddress = hostdic[HOST_CFG_KEY_IP]
        
        authProtocol = None 
        privProtocol = None    
        if 'SHA'.find(hostdic[HOST_CFG_KEY_AUTHPROTOCOL]) != -1:
            authProtocol = usmHMACSHAAuthProtocol
        else:
            authProtocol = usmHMACMD5AuthProtocol
        if 'AES'.find(str(hostdic[HOST_CFG_KEY_PRIVPROTOCOL])) != -1:
            privProtocol = usmAesCfb128Protocol
        else:
            privProtocol = usmDESPrivProtocol 
        try:    
            if 'v3' == hostdic[HOST_CFG_KEY_SNMPVERSION].lower():
                errorIndication, errorStatus, errorIndex, varBinds = \
                        cmdgen.CommandGenerator().getCmd(cmdgen.UsmUserData(\
                                                   hostdic[HOST_CFG_KEY_USER], \
                                                   hostdic[HOST_CFG_KEY_PASS], \
                                                   hostdic[HOST_CFG_KEY_PASS], \
                                                   authProtocol, \
                                                   privProtocol ), \
                                            cmdgen.UdpTransportTarget(\
                                                   (ipaddress, \
                                                    hostdic[HOST_CFG_KEY_PORT])), typeoid)  
            else:
                errorIndication, errorStatus, errorIndex, varBinds = \
                        cmdgen.CommandGenerator().getCmd(
                                    cmdgen.CommunityData(hostdic[HOST_CFG_KEY_COMMUNITY]), \
                                    cmdgen.UdpTransportTarget(\
                                            (ipaddress, hostdic[HOST_CFG_KEY_PORT])), \
                                           typeoid)         
            type = None
            if errorIndication is None \
                            and errorStatus == 0 \
                            and errorIndex == 0:
                if param == "enginid":
                     
                    type = str(varBinds).split("'")[1]
                else:
                    for varoid, vartype in varBinds:
                        oid = str(varoid)
                        type = str(vartype)
                        if oid == typeoid and not type is None and type != '':
                            return type
                    # 不支持CH系列刀片
                    return None
                return type
            else:
                return None
        except Exception, error:
            logger.error("getHostType exception error info=%s"%(str(err)) )         
            return None 
class ConfigException(Exception):
    '''
    ' 配置异常
    '''
    pass

if __name__ == '__main__':
    Initialization().start()
