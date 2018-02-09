#encoding:utf-8

#采集功能启动方式
COLLECT_MODE_CMD_PLUGIN = 1;   #插件启动，采集默认配置模板BASIC信息
COLLECT_MODE_CMD_TOTAL = 2;    #命令行启动，采集默认配置模板所有信息
COLLECT_MODE_CMD_FILE = 3;     #命令行启动，采集指定配置模板所有信息


#字符串常量
NAGIOS_STATUS_UNKNOWN = "3";
NAGIOS_INFORMATION_UNKNOWN = "Unknown";
NAGIOS_INFORMATION_SEP = " "
NAGIOS_CMD = "[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%s;%s\n"


#数字常量
NUMBER_ZERO = 0;
NUMBER_ONE = 1;
NUMBER_TWO = 2;
NUMBER_THREE = 3;
NUMBER_FOUR = 4;
NUMBER_FIVE = 5;



#错误码

NAGIOS_ERROR_SUCCESS = 0;                      #操作成功
NAGIOS_ERROR_FAILED = 1;                       #操作失败
NAGIOS_ERROR_INVALID_TARGET = 3                #无效的IP或端口
NAGIOS_ERROR_INVALID_ENGINE = 4                #无效的SNMP引擎
NAGIOS_ERROR_INVALID_METHOD = 5                #无效的SNMP请求方式
NAGIOS_ERROR_HOST_CONFIG_NOTEXIST = 6          #host配置文件不存在
NAGIOS_ERROR_HOST_FORMAT_INVALID = 7           #host配置文件格式不合法
NAGIOS_ERROR_DEVICE_XML_INVALID = 8            #设备配置文件不存在
NAGIOS_ERROR_DEVICE_CONFIG_NOTEXIST = 9        #设备采集配置文件不存在
NAGIOS_ERROR_DEVICE_FORMAT_INVALID = 10        #设备采集配置文件格式不合法
NAGIOS_ERROR_DEVICE_CONFIG_NOTINCLUDE = 11     #设备采集配置文件中不包含服务模块
