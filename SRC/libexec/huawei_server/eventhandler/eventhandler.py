# coding=utf-8

'''
' Created on 2013-3-15
' 
' Trap message handler for nagios.

'''

import os
import re
import time
import logging


##########################################################################
# 常量定义
##########################################################################
SENSOR_KEY = 'Sensor'
AGENTIP_KEY = 'Agent Address'
EVENTINFO_KEY = 'Event'
STATUS_KEY = 'Severity'
EVENTCODE_KEY = 'Event Code'
CODE_KEY = 'Code'
DESCRIPTION_KEY = 'Description'
TIMESTAMP_KEY = 'Time'
CHASSIS_KEY = 'Chassis Serial#'
LOCATION_KEY = 'Location'
BLADE_KEY = 'Blade'
PROPERTY_COUNT_SMM = 8
PROPERTY_COUNT_BMC = 5
RTC_FAULT = "RTC Fault"

STATUS_WARN_PATTERN ='^.*Deassertion.*$'
STATUS_OK_STR_PATTERN = '^.*Assertion.*OK.*$'
STATUS_NORMAL_PATTERN = '^.*Assertion.*Normal.*$'
STATUS_INFO_PATTERN = '^.*Assertion.*Info.*$'
STATUS_OK_STR = 'OK'
STATUS_OK_INT = 0
STATUS_MINOR_STR_PATTERN = '^.*Assertion.*Minor.*$'
STATUS_MINOR_INT = 1
STATUS_WARNING_STR_PATTERN = '^.*Assertion.*Warning.*$'
STATUS_WARNING_INT = 1
STATUS_MAJOR_STR_PATTERN = '^.*Assertion.*Major.*$'
STATUS_MAJOR_INT = 2
STATUS_CRITICAL_STR_PATTERN = '^.*Assertion.*Critical.*$'
STATUS_CRITICAL_INT = 2
STATUS_UNKNOWN_STR_PATTERN = '^.*Assertion.*Unknown.*$'
STATUS_UNKNOWN_STR = 'Unknown'
STATUS_UNKNOWN_INT = 3

EVENT_CODE_PATTERN = '0x([a-fA-F0-9]{8})'
IP_ADDRESS_FORMAT = \
    '^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.' + \
    '(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.' + \
    '(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.' + \
    '(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])$'

TRAP_BINDING_VALUE_SEP = "[,;/-]"
BINDING_KEY_VALUE_SEP = ':'
CMD_FILE_NAME_SEP = '_'
CMD_FILE_CONTENT_SEP = '&'
NAGIOS_CMD_SEP = ';'
NAGIOS_CMD_SIGN = 'PROCESS_SERVICE_CHECK_RESULT'
NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT = '['
NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT = ']'

BINDING_VALUE_PATTERN = '(%s|%s|%s|%s|%s|%s|%s|%s|%s|%s)%s(.*)' \
                        % (CHASSIS_KEY, LOCATION_KEY, BLADE_KEY, \
                           SENSOR_KEY, EVENTINFO_KEY, STATUS_KEY, \
                           EVENTCODE_KEY, TIMESTAMP_KEY, \
                           DESCRIPTION_KEY,CODE_KEY,BINDING_KEY_VALUE_SEP)




logger = logging.getLogger('huawei_plugin.handler')


class HandlerFactory(object):
    '''
    ' 处理器工厂
    ' methods: 
    '     createHandler: 静态方法，通过解析trap的事件码，
    '                    区别trap类型，构造相应处理器
    '''

    def createHandler(agentip, varBinds, configdata):
        '''
        ' 静态方法，创建相应的处理器实例
        ' params:
        '     agentip: 发送trap消息的agent的地址
        '     varBinds: trap消息绑定值
        '     configdata: 配置数据实例
        ' return GenericHandler: 特定的处理器实例
        ' raise TrapException: 当消息不正确时抛出
        '''
        logger.info('=================================================')
        if len(varBinds) < 1:
            raise TrapException('Message invalid. Not binding values. ')
        if agentip is None or re.match(IP_ADDRESS_FORMAT, agentip) is None:
            raise TrapException( \
                'Message invalid. Must have a valid ip address of agent. ')
        if not agentip in configdata.Hostdata.keys():
            raise TrapException('Not managed host: ' + agentip)
        trapdata = TrapData(agentip, varBinds, configdata)
        logger.info('=================TrapData handle end================================')
        if trapdata.isWarning():
            # 告警级别为0被认为是事件, 暂不报告事件(无服务器型号的完整事件定义)
            if trapdata.Status == STATUS_OK_INT:
                raise UnSupportedException('Event trap. Not handle. ')
            logger.info('Instance warning handler. ')
            return WarningTrapHandler(trapdata)
        else:
            logger.info('Instance warning cleared handler. ')
            return WarningClearedTrapHandler(trapdata)

    createHandler = staticmethod(createHandler)


class GenericHandler(object):
    '''
    ' Trap信息处理器基类
    ' methods:
    '     handle: 虚方法
    '     getTrapdata: 返回trapdata实例
    '''

    def __init__(self, trapdata):
        try:
            hostname = trapdata.getHostName()
            timestamp = trapdata.getTimestamp()
            if hostname is None or timestamp is None or hostname == '':
                raise PluginException('Trap data is invalid. ')
            logger.info('begin getting service Description.')
        
        except:
            raise
        self._trapdata = trapdata
        self._filehandler = FileHandler(trapdata.Configdata.Cachepath)
        self._nagioscorresponder = NagiosCorresponder( \
            trapdata.Configdata.Cmdfilepath)

    def handle(self):
        '''
        ' 虚方法，处理Trap信息
        '''
        pass

    def getTrapdata(self):
        '''
        ' 获取trap数据实例
        ' return TrapData: trap消息的数据实例
        '''
        return self._trapdata


class WarningTrapHandler(GenericHandler):
    '''
    ' 告警Trap处理器
    ' methods:
    '     handle: 处理告警类trap, 
    '             记录告警文件并完全处理所有告警并叠加信息并传输给Nagios进行呈现
    '''

    def __init__(self, trapdata):
        super(WarningTrapHandler, self).__init__(trapdata)

    def handle(self):
        '''
        ' 记录告警文件并完全处理所有告警并叠加信息并传输给Nagios进行呈现
        '''
        logger.info('Handle warning trap...')
        self._filehandler.saveWarningFile(self._trapdata)
        status, info = self._filehandler.handleWarningFiles(self._trapdata)
        self._nagioscorresponder.correspond(self._trapdata, status, info)
        logger.info('Handle warning trap complete. ')


class WarningClearedTrapHandler(GenericHandler):
    '''
    ' 解除告警Trap处理器
    ' methods:
    '     handle: 处理解除告警类trap信息, 
    '             删除这类告警的所有告警文件并传输给Nagios进行呈现
    '''

    def __init__(self, trapdata):
        super(WarningClearedTrapHandler, self).__init__(trapdata)

    def handle(self):
        '''
        ' 删除这类告警的所有告警文件并传输给Nagios进行呈现
        '''
        logger.info('Handle warning_cleared trap...')
        self._filehandler.clearWarningFiles(self._trapdata)
        status, info = self._filehandler.handleWarningFiles(self._trapdata)
        self._nagioscorresponder.correspond(self._trapdata, status, info)
        logger.info('Handle warning_cleared trap complete. ')


class FileHandler(object):
    '''
    ' 缓存文件处理器
    ' methods:
    '     saveWarningFile: 将告警trap保存为缓存文件
    '     clearWarningFiles: 当接收解除告警trap时，删除该类告警文件
    '     handleWarningFiles: 处理所有当前类型的告警文件, 叠加告警信息
    '''

    def __init__(self, filecachepath):
        self._filecachepath = filecachepath

    def saveWarningFile(self, trapdata):
        '''
        ' 将告警保存为文件'
        ' params:
        '     trapdata: 当前trap数据实例'
        ' raise PluginException: 当文件读写失败, 或一些未知异常时抛出(如权限问题)
        '''
        filepath = self._constructFullFilename(trapdata, \
                                               self._constructFilename(trapdata))
        try:
            info = trapdata.Info
            if not trapdata.Blade is None and '' != trapdata.Blade:
                info = info + '(' + trapdata.Blade + ')'
            msg = str(trapdata.Status) + CMD_FILE_CONTENT_SEP + info
            file = open(filepath, 'w')
            file.write(msg)
        except IOError, err:
            raise PluginException('Write warning file error. Cause: \n' \
                                  + str(err))
            file.close()
        except Exception, err:
            raise PluginException( \
                'Unknown error when writing warning file. Cause: \n' \
                + str(err))
            file.close()
        else:
            file.close()

    def clearWarningFiles(self, trapdata):
        '''
        ' 清理指定的所有告警文件
        ' params:
        '     trapdata: 当前trap数据实例
        ' raise PluginException: 当删除文件出错时抛出
        '''
        try:
            for filename in os.listdir(self._filecachepath):
                if filename.startswith(self._constructFilename(trapdata, \
                                                               withtime=False, \
                                                               towarning=True)):
                    os.remove(self._constructFullFilename(trapdata, filename))
            logger.info('Removed all warning files. ')
        except Exception, err:
            raise PluginException('Clear warning files error. Cause: \n' \
                                  + str(err))

    def handleWarningFiles(self, trapdata):
        '''
        ' 处理所有告警文件并汇总，告警状态为最高值，告警信息逐行叠加
        ' params:
        '     trapdata: 当前trap数据实例
        ' return tuple: 由该类所有告警中的最高级别和所有告警信息叠加组成的元组
        ' raise PluginException: 当操作文件异常或其他数据异常时抛出
        '''
        statuslst = []
        info = ''
        try:
            warningfiles = os.listdir(self._filecachepath)
            if warningfiles is None or len(warningfiles) < 1:
                return (STATUS_OK_INT, STATUS_OK_STR)
            file = None
            temp = 0
            warnList=[]
            for filename in warningfiles:
                agentip = filename.split(CMD_FILE_NAME_SEP)[0]
                eventcode = filename.split(CMD_FILE_NAME_SEP)[1]
                sensor = filename.split(CMD_FILE_NAME_SEP)[2]
                WarnId=eventcode+sensor
                #do not display same warning 
                if WarnId in warnList:
                    continue
                warnList.append(WarnId)
                #去掉warning 白名单
                if  trapdata.Agentip == agentip:
                    file = open(self._constructFullFilename(trapdata, filename), \
                                'r')
                    fileline = file.readline()
                    statuslst.append(int(fileline.split( \
                        CMD_FILE_CONTENT_SEP)[0]))
                    temp += 1
                    info = info + str(temp) + "." \
                           + fileline.split(CMD_FILE_CONTENT_SEP)[1] \
                           + ';  '
                    file.close()
            if len(statuslst) < 1:
                return (STATUS_OK_INT, STATUS_OK_STR)
            statuslst.sort(reverse=True)
            return (statuslst[0], info)
        except IOError, err:
            raise PluginException('Read warning file error. Cause: \n' \
                                  + str(err))
            if not file is None:
                file.close()
        except Exception, err:
            raise PluginException( \
                'Unknown error when reading warning file. Cause: \n' \
                + str(err))
            if not file is None:
                file.close()
        else:
            if not file is None:
                file.close()

    def _constructFullFilename(self, trapdata, filename):
        '''
        ' 构造完整的告警文件路径名
        ' params:
        '     trapdata: 当前trap数据实例
        '     filename: 文件短名
        ' return str: 文件的完整路径名
        '''
        return self._filecachepath + os.path.sep + filename

    def _constructFilename(self, trapdata, withtime=True, towarning=False):
        '''
        ' 构造告警文件名
        ' params:
        '     trapdata: 当前trap数据实例
        '     withTime: 构造的文件名是否需要带告警时间戳
        ' return str: 由时间(可选)事件码和传感器名称组成的文件名
        '''
        if towarning:
            filename = trapdata.Agentip \
                       + CMD_FILE_NAME_SEP \
                       + trapdata.toWarningCodeWithWarningCleared() \
                       + CMD_FILE_NAME_SEP \
                       + trapdata.Sensor
        else:
            filename = trapdata.Agentip \
                       + CMD_FILE_NAME_SEP \
                       + trapdata.getCodeStr() \
                       + CMD_FILE_NAME_SEP \
                       + trapdata.Sensor
        if not trapdata.Blade is None and '' != trapdata.Blade:
            filename = filename + CMD_FILE_NAME_SEP + trapdata.Blade
        if withtime:
            filename = filename \
                       + CMD_FILE_NAME_SEP \
                       + str(trapdata.getTimestamp())
        return filename


class NagiosCorresponder(object):
    '''
    ' Nagios通信器, 将告警信息传输给Nagios, 让其呈现
    ' methods:
    '     correspond: 传输数据, 以Nagios要求的形式, 
    '                 将告警信息格式化并写入到Nagios指定的文件中
    '''

    def __init__(self, cmdfilepath):
        self._cmdfilepath = cmdfilepath

    def correspond(self, trapdata, status, info):
        '''
        ' 将最终的告警状态和告警信息汇报给nagios，让其进行呈现
        ' params:
        '     trapdata: 当前告警数据实例
        '     status: 该类告警的最高级别
        '     info: 所有该类告警信息叠加
        '''
        try:
            nagiosmsg = self._constructMessage(trapdata, status, info)
            file = open(self._cmdfilepath, 'a')
            file.write(nagiosmsg)
        except IOError, err:
            raise PluginException('Write to cmdfile of nagios error. Cause: \n' \
                                  + str(err))
            file.close()
        except Exception, err:
            raise PluginException('Write to cmdfile of nagios error. Cause: \n' \
                                  + str(err))
            file.close()
        else:
            file.close()

    def _constructMessage(self, trapdata, status, info):
        '''
        ' 构造与Nagios通信的消息
        ' params:
        '     trapdata: 当前trap数据实例
        '     status: 当前告警最高级别
        '     info: 该类所有存在的告警描述
        ' return str: 符合Nagios插件接口要求的外部命令字符串
        '''
        # 解决市区问题，放弃trap自带时间 str(trapdata.getTimestamp())使用time.time()
        
        return NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT \
               + str(time.time()) \
               + NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT + ' ' \
               + NAGIOS_CMD_SIGN + NAGIOS_CMD_SEP \
               + trapdata.getHostName() + NAGIOS_CMD_SEP \
               + 'alarm' + NAGIOS_CMD_SEP \
               + str(status) + NAGIOS_CMD_SEP \
               + info \
               + '\n'


class TrapData(object):
    '''
    ' Trap信息数据
    ' methods:
    '     matchingSensorName: 使用传感器名称正则匹配当前trap中的传感器名称
    '     matchingEventCode: 匹配事件码
    '     matchingService: 匹配服务，
    '                     通过给定的事件码和传感器判断确定的告警所属服务
    '                     是否与当前trap描述的告警的所属服务相同
    '     isWarning: 检查当前trap是否为告警
    '     getWarningClearedCode: 通过告警事件码获取这类告警的解除事件码
    '     getServiceDescription: 通过传感器名称和事件码确定告警, 
    '                            再通过配置文件确定监控服务名称
    '     getHostName: 获取发送trap的主机名称
    '     getHostType: 获取发送trap的主机型号
    '     getTimestamp: 获取告警时间的时间戳
    '     getCodeStr: 获取事件码的16进制字符串
    '     getStatus: 获取告警级别对应的值
    ' properties:
    '     Configdata: 配置数据实例
    '     Agentip: 发送当前trap的agent的地址
    '     Time: 当前trap的告警/解除告警时间
    '     Code: 当前trap的告警/解除告警事件码
    '     Sensor: 当前trap的告警/解除告警的传感器名称
    '     Info: 当前trap的告警/解除告警的告警信息
    '     Status: 当前trap的告警的级别
    '''

    def __init__(self, agentip, varBinds, configdata):
        self._configdata = configdata
        self._agentip = agentip
        self._time = None
        self._code = None
        self._sensor = None
        self._info = None
        self._status = None
        self._chassis = None
        self._blade = None
        self._location = None
        self._parseTrapMsg(varBinds)
    
      
  
    def matchingSensorName(self, sensorpattern, sensor=None):
        '''
        ' 匹配传感器名称
        ' params:
        '     sensorpattern: 传感器名称匹配正则式
        '     sensor: 待匹配传感器名称
        ' return boolean: 是否匹配
        '''
        sensorname = self._sensor
        if not sensor is None:
            sensorname = sensor
        if re.match(sensorpattern, sensorname):
            return True
        return False

    def matchingEventCode(self, eventcode, eventcodematching):
        '''
        ' 匹配事件码
        ' params:
        '     eventcode: 待匹配的事件码
        '     eventcodematching 匹配事件码
        ' return boolean: 是否匹配
        '''
        eventcodetmp = self.getCodeStr().upper()
        if not eventcodematching is None:
            eventcodetmp = eventcodematching
        if eventcodetmp.upper().endswith(eventcode.upper()):
            return True
        return False
 
   #判断是否告警恢复
    def isWarning(self):
        '''
        ' 根据告警的事件码判断这个Trap是告警还是解除告警
        ' return boolean: 若是告警返回True, 解除告警返回False
        ''' 
        if not re.match(STATUS_WARN_PATTERN, self._status) is None:
            return False
        else:
           
            return True
    #判断是否是新告警恢复
    def isNewRecoveryWarn(self): 
         if self.isWarning() == False:         
             bincode=hex2bin(self.getCodeStr()).zfill(32)
             if bincode[8]=='1':
                  return False
             else: 
                  return True
         else:
            return False

    def toWarningCodeWithWarningCleared(self):
        '''
        ' 根据告警的事件码计算该告警的解除告警事件码
        ' (第二字节最高位字节如果为0是告警，为1是解除告警)
        ' return str: 对应告警的解除告警事件码16进制字符串
        '''
        EventCode = self.getCodeStr()  
        if self.isNewRecoveryWarn():            
             recoveryCode=int(hex2dec(EventCode))-1          
             return dec2hex(str(recoveryCode)).zfill(8) 
        else :  
             bincode = list(hex2bin(EventCode).zfill(32))
             bincode[8] = '0'
             return bin2hex(''.join(bincode)).zfill(8)

    def getHostName(self):
        '''
        ' 根据配置文件，读取Agent IP对应的用户定义的主机名称
        ' return str: 主机名称
        '''
        return self._configdata.getHostName(self._agentip)

    def getHostType(self):
        '''
        ' 根据配置文件，读Agent IP对应的用户定义的主机型号
        ' return str: 主机型号
        '''
        return self._configdata.getHostType(self._agentip)

    def getConfigdata(self):
        '''
        ' 获取配置数据
        ' return ConfigData: 配置数据
        '''
        return self._configdata

    def getAgentip(self):
        '''
        ' 获取agent地址
        ' return str: agent的ip地址
        '''
        return self._agentip

    def getTime(self):
        '''
        ' 获取告警时间
        ' return str: 告警时间
        '''
        return self._time

    def getTimestamp(self):
        '''
        ' 获取告警时间的时间戳形式
        ' return double: 告警时间戳
        '''
        # 由于时区问题，使用服务器时间，初始化的时候，即使用trap接收时的当前时间
        return self._time

    def getCode(self):
        '''
        ' 获取告警事件码
        ' return str: 告警事件码
        '''
        return self._code

    def getCodeStr(self):
        '''
        ' 获取告警16进制字符串的事件码
        ' return str: 16进制字符串形式的告警事件码
        '''
        return re.match(EVENT_CODE_PATTERN, self._code).group(1).upper()

    def getSensor(self):
        '''
        ' 获取传感器名称
        ' return str: 传感器名称
        '''
        return self._sensor

    def getInfo(self):
        '''
        ' 获取告警描述信息
        ' return str: 告警描述信息
        '''
        return self._info

    def getBlade(self):
        '''
        ' 获取刀片名称
        ' return str: 刀片名
        '''
        return self._blade

    def getChassis(self):
        '''
        ' 获取刀片序列号
        ' return str: 刀片序列号
        '''
        return self._chassis

    def getLocation(self):
        '''
        ' 获取位置
        ' return str: 位置
        '''
        return self._location

    def getStatus(self):
        '''
        ' 获取各种监控状态值
        ' return int: 告警级别对应的值: 
        '             0=OK; 1=Minor; 2=Major,Critical; 3=Unknown
        '''
        if not re.match(STATUS_OK_STR_PATTERN+"|"+STATUS_NORMAL_PATTERN+"|"+STATUS_INFO_PATTERN, self._status) is None:
            return STATUS_OK_INT
        elif not re.match(STATUS_MINOR_STR_PATTERN, self._status) is None:
            return STATUS_MINOR_INT
        elif not re.match(STATUS_MAJOR_STR_PATTERN, self._status) is None \
                or not re.match(STATUS_CRITICAL_STR_PATTERN, \
                                self._status) is None:
            return STATUS_CRITICAL_INT
        else:
            return STATUS_UNKNOWN_INT

    def _parseTrapMsg(self, varBinds):
        '''
        ' 解析trap信息
        ' params:
        '     varBinds: 当前trap的绑定值
        '''
        bindingvalues = self._parseBindingValuesMsg(varBinds)
        bindingvalues = self._preHandlerE6000(bindingvalues)
        trapdic = self._parseBindingValues(bindingvalues)
        # 时区问题，使用服务器当前时间初始化
        self._time = time.time()
        if(trapdic.__contains__(EVENTCODE_KEY)):
            self._code = trapdic.get(EVENTCODE_KEY).lower()
        else:
            self._code = trapdic.get(CODE_KEY).lower()
            
        if(trapdic.__contains__(SENSOR_KEY)):
            self._sensor = trapdic.get(SENSOR_KEY)
            
        if(trapdic.__contains__(EVENTINFO_KEY)):
            self._info = trapdic.get(EVENTINFO_KEY)
        else:
            self._info = trapdic.get(DESCRIPTION_KEY)   
             
        if(trapdic.__contains__(STATUS_KEY)):
            self._status = trapdic.get(STATUS_KEY)
        if(trapdic.__contains__(CHASSIS_KEY)):    
            self._chassis = trapdic.get(CHASSIS_KEY)
        if(trapdic.__contains__(BLADE_KEY)):    
            self._blade = trapdic.get(BLADE_KEY)
        if(trapdic.__contains__(LOCATION_KEY)):    
            self._location = trapdic.get(LOCATION_KEY)

    def _parseBindingValuesMsg(self, varBinds):
        '''
        ' 解析出绑定值字符串
        ' params:
        '     varBinds: 绑定值表
        ' return str: 绑定值字符串
        '''
        standardmsg = ''
        for oid, val in varBinds:
            if oid.prettyPrint() == self._configdata.getBindingValuesOID():
                standardmsg = val.prettyPrint().strip()
        if standardmsg is None or standardmsg == '':
            raise TrapException('Not valid binding value. ')
        return standardmsg.strip()

    def _parseBindingValues(self, standardmsg):
        '''
        ' 解析绑定值字符串
        ' params:
        '     standardmsg: 绑定值字符串
        ' return dic: 绑定值字典
        '''
        # 通过是否存在Blade属性判断是SMM还是BMC发出的Trap
        propertycount = -1
        if -1 == standardmsg.find(BLADE_KEY):
            propertycount = PROPERTY_COUNT_BMC
        else:
            propertycount = PROPERTY_COUNT_SMM
        bindingpattern = (TRAP_BINDING_VALUE_SEP +" *").join([BINDING_VALUE_PATTERN \
                                     for i in range(propertycount)])
        
        matcher = re.match(bindingpattern, standardmsg)
        if matcher is None:
            raise TrapException('Binding value is invalid. ')
        trapdic = {}
        for i in range(propertycount):
            keyindex = 2 * i + 1
            valueindex = 2 * i + 2
            key = matcher.group(keyindex)
            value = matcher.group(valueindex)
            if key is None or key == '':
                break
            trapdic[key.strip()] = value.strip()
        return trapdic

    def _preHandlerE6000(self, bindingvalues):
        '''
        ' E6000预处理
        ' params:
        '     standardmsg: 绑定值字符串
        ' return str: 预处理后的标准绑定值
        '''
        logger.info('PreHandle trap for E6000...')
        propertycount = 8
        bindingpattern = '(Time):(.*)%s *(Location):(.*)%s *(Chassis Serial # ):(.*)%s *(Blade):(.*)%s *(Sensor):(.*)%s *(Event):(.*(Assertion:|Deassertion,)(.*))%s *(Event Code ):(.*)'%(TRAP_BINDING_VALUE_SEP,TRAP_BINDING_VALUE_SEP,TRAP_BINDING_VALUE_SEP,TRAP_BINDING_VALUE_SEP,TRAP_BINDING_VALUE_SEP,TRAP_BINDING_VALUE_SEP)
        matcher = re.match(bindingpattern, bindingvalues)
        if matcher is None:
            return bindingvalues
        trapdic = {}
        for i in range(propertycount):
            keyindex = 2 * i + 1
            valueindex = 2 * i + 2
            key = matcher.group(keyindex)
            value = matcher.group(valueindex)
            if key is None or key == '':
                raise TrapException('Binding value is invalid. ')
            if key.find(':') != -1 or key.find(',') != -1:
                value = '%s [%s]' % (key.replace(':', '').replace(',', '').strip(), value.strip())
                key = 'Severity'
            trapdic[key.strip()] = value.strip()
        logger.info('PreHandle trap of E6000 complete. ')
        return 'Time:%s,Location:%s,Chassis Serial#:%s,Blade:%s,Sensor:%s,Event:%s,Severity:%s,Event Code:%s' \
               % (trapdic.get('Time'), trapdic.get('Location'), \
                  trapdic.get('Chassis Serial #'), trapdic.get('Blade'), \
                  trapdic.get('Sensor'), trapdic.get('Event'), \
                  trapdic.get('Severity'), trapdic.get('Event Code'))

    Configdata = property(fget=getConfigdata)
    Agentip = property(fget=getAgentip)
    Time = property(fget=getTime)
    Code = property(fget=getCode)
    Sensor = property(fget=getSensor)
    Info = property(fget=getInfo)
    Status = property(fget=getStatus)
    Blade = property(fget=getBlade)
    Chassis = property(fget=getChassis)
    Location = property(fget=getLocation)


class TrapException(Exception):
    '''
    ' Trap信息相关异常
    '''
    pass


class UnSupportedException(Exception):
    '''
    ' 插件无法支持异常, 如型号不支持等
    '''
    pass


class PluginException(Exception):
    '''
    ' 插件异常
    '''
    pass


######################################################################
# 
# 工具方法
# 
######################################################################
base = [str(x) for x in range(10)] \
       + [chr(x) for x in range(ord('A'), ord('A') + 6)]


def hex2bin(string_num):
    '''
    ' 十六进制转二进制
    '''
    return dec2bin(hex2dec(string_num.upper()))


def bin2hex(string_num):
    '''
    ' 二进制转十六进制
    '''
    return dec2hex(bin2dec(string_num))


def dec2bin(string_num):
    '''
    ' 十进制转二进制
    '''
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num, rem = divmod(num, 2)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])


def bin2dec(string_num):
    '''
    ' 二进制转十进制
    '''
    return str(int(string_num, 2))


def dec2hex(string_num):
    '''
    ' 十进制转十六进制
    '''
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num, rem = divmod(num, 16)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])


def hex2dec(string_num):
    '''
    ' 十六进制转十进制
    '''
    return str(int(string_num.upper(), 16))

def convertClearAlarmId(eventIdStr):
    '''
    ' 转化恢复告警
    '''
    eventIdL = long('1' + eventIdStr[2:],16)
    if RTC_FAULT == eventIdStr[2:]:
        incrementL = long("00010000", 16)
        clearEventIdstr = dec2hex(str(eventIdL + incrementL))
    else:
        incrementL = long("00800000", 16)
        clearEventIdstr = dec2hex(str(eventIdL - incrementL)) 
    return clearEventIdstr

  
   
   
