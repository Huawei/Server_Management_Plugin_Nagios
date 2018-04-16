#coding=utf-8
import os
import sys
import commands
import time
import re
from optparse import OptionParser

from getInfoForBlade import InfoHandler as bladeInfoHandler
from getInfo import InfoHandler as rackInfoHandler
from getInfoForBlade import MSG_HEASTATUS

STATUS_UNKNOWN=3
COMPONENT_POWER="power"
COMPONENT_BLADE="blade"
COMPONENT_FAN="fan"
COMPONENT_SYS= "system"
COMPONENT_SWI="switch"
COMPONENT_SMM="smm"
COMPONENT_SHELF="shelf"
COMPONENT_CPU="cpu"
COMPONENT_MEMORY="memory"
COMPONENT_DISK="hardDisk"
COMPONENT_RAID="raid"

def find_nagiosdir():
    '''return nagios directory'''
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)
    return procs
nagiosHome = find_nagiosdir()
genkeyPath=nagiosHome+ os.path.sep +"bin"+ os.path.sep +"huawei_server"
sys.path.append(genkeyPath)

TRAP_BINDING_VALUE_SEP = "[,;/-]"
BINDING_KEY_VALUE_SEP = ':'
CMD_FILE_NAME_SEP = '_'
CMD_FILE_CONTENT_SEP = '&'
NAGIOS_CMD_SEP = ';'
NAGIOS_CMD_SIGN = 'PROCESS_SERVICE_CHECK_RESULT'
NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT = '['
NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT = ']'


def constructMessage(host , service , status , info):        
    return NAGIOS_CMD_TIMESTAMP_SURROUND_LEFT \
               + str(time.time()) \
               + NAGIOS_CMD_TIMESTAMP_SURROUND_RIGHT + ' ' \
               + NAGIOS_CMD_SIGN + NAGIOS_CMD_SEP \
               + host + NAGIOS_CMD_SEP \
               + service + NAGIOS_CMD_SEP \
               + str(status) + NAGIOS_CMD_SEP \
               + info \
               + '\n'
def getCmdfilePath():
    initfilePath=os.path.normpath(sys.path[0])+"/../.." + os.path.sep + "etc" + os.path.sep+"huawei_server/initial.cfg"
    initial_cfg = open(initfilePath)
    for pro in initial_cfg:
        if re.findall(r'^\s*nagios_cmd_file\s*=\s*/', pro):
            nagioscmd_file= re.sub(r'\s*$','',pro.split('=')[1])  
    if  not  nagioscmd_file == None:     
        return nagioscmd_file
    else: return None               
def writeCmd( host , service , status , info) :
    file=None
    try:
        file = open( getCmdfilePath(), 'a')
        nagioscmd=constructMessage(host , service , status , info)
        file.write(nagioscmd)
    except Exception,err:
        print "writeCmd error: " +str(err)
    finally:
        if file is not None:
            file.close()

def dencrypt(str):
    from genKey import readKey 
    from genKey import genRootKeyStr
    from genKey import dencryptKey
   
    k=dencryptKey(readKey(),genRootKeyStr())
    decryotStr=dencryptKey(str,k )
    
    if decryotStr is None:
        return ''
    else :
        return decryotStr    

def commandParse():
    opts={}
    parser = OptionParser()
    parser.add_option("-c","--component", dest="component", 
        help="component for check  as (hardDisk,cpu,memory,power,cpu,memory,fan,system,hardDisk)",default="system")
    parser.add_option("-H","--host", dest="host", 
        help="Hostname or IP address of the host to check",default=None)
    parser.add_option("-v","--version", dest="version",
        help="SNMP Version to use (1, 2c or 3)", default="3")
    parser.add_option("-u","--user", dest="user",
        help="SNMP username (only with SNMP v3)", default= None)
    parser.add_option("-C","--community", dest="community",
        help="SNMP Community (only with SNMP v1|v2c)", default=None)
    parser.add_option("-p","--port", dest="port",
        help="port for SNMP", default="161")    
    parser.add_option("-A","--apwd", dest="apwd",
        help="SNMP authentication password (only with SNMP v3)", default=None)
    parser.add_option("-a","--aprotocol", dest="aprotocol",
        help="SNMP authentication protocol (SHA only with SNMP v3)", default="SHA")
    parser.add_option("-X","--ppwd", dest="ppwd",
        help="SNMP privacy password (only with SNMP v3)", default=None)
    parser.add_option("-x","--pprotocol", dest="pprotocol",
        help="SNMP privacy protocol AES||DES (only with SNMP v3)", default='AES')
    parser.add_option("-l","--seclevel", dest="seclevel",
        help="SNMP security level (only with SNMP v3) (noAuthNoPriv|authNoPriv|authPriv)", default="authPriv")
    parser.add_option("-t","--timeout", dest="timeout",
        help="Timeout in seconds for SNMP", default="10") 
    parser.add_option("-T","--type", dest="type",
        help="service types as (blade, rack)", default="blade")  
    parser.add_option("-r","--retry", dest="retry",
        help="Timeout in seconds for SNMP", default="2")
    (opts,args) = parser.parse_args()
    compenlist=[COMPONENT_POWER,COMPONENT_FAN,COMPONENT_SYS\
    ,COMPONENT_SWI,COMPONENT_SMM,COMPONENT_SHELF,COMPONENT_BLADE]
    if opts.type.upper() == "RACK" or  opts.type.upper() == "HIGHDENSITY":
        compenlist=[COMPONENT_POWER,COMPONENT_FAN,COMPONENT_SYS\
    ,COMPONENT_CPU,COMPONENT_MEMORY,COMPONENT_DISK ,COMPONENT_RAID]
    if  opts.host== None :
        print  "please input Hostname or IP "
        exit(STATUS_UNKNOWN)
    if  opts.version== '3' and  opts.user== None :
        print  "please input SNMP username  "
        exit(STATUS_UNKNOWN)  
    if  opts.ppwd== None :
        opts.ppwd = opts.apwd  
    if not opts.component in compenlist:
        print  " -c  only support as : " 
        for  eachitem in compenlist:
            print eachitem
        exit(STATUS_UNKNOWN)   
    if not opts.apwd is None:
        opts.apwd = dencrypt ( opts.apwd)
    if not opts.ppwd is None:
        opts.ppwd = dencrypt ( opts.ppwd)
    if not opts.community is None:
        opts.community = dencrypt ( opts.community)
    
    return opts 

if __name__ == '__main__':  
    opts=commandParse() 

    try :
        if  opts.type.lower() =='blade':
            infoHandler= bladeInfoHandler(opts)
            status ,info = infoHandler.getAllStatus( infoHandler._Parm.component) 
            writeCmd(infoHandler._Parm.host, infoHandler._Parm.component.lower(),status,\
            ("%s HealthStatus: %s "% ( str(infoHandler._Parm.component) ,MSG_HEASTATUS[status]))+info.replace('\n',"====") )
        else :
            infoHandler= rackInfoHandler(opts)
            status ,info = infoHandler.getRaidStatus() 

        print "%s HealthStatus: %s "% ( str(infoHandler._Parm.component) ,MSG_HEASTATUS[status])
        print "=============================== info ============================="
        print info
        exit(status)     
    except Exception, e:
        print "Unhandled exception while running script: %s" % e
        exit(STATUS_UNKNOWN)
