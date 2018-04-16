#coding=utf-8

from optparse import OptionParser
import os
import re
import sys
import subprocess
import logging
import logging.handlers as handlers
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
                                                + 'getInfoForBlade.log', \
                                                        when='midnight', \
                                                        interval=1, \
                                                        backupCount=30)
filehandler.setLevel(logging.INFO)
errorfilehandler = logging.FileHandler(os.path.dirname(__file__) + os.path.sep \
                                       + 'getInfoForBlade_error.log')
errorfilehandler.setLevel(logging.ERROR)
consolehandler.setFormatter(formatter)
filehandler.setFormatter(formatter)
errorfilehandler.setFormatter(formatter)
logger.addHandler(consolehandler)
logger.addHandler(filehandler)
logger.addHandler(errorfilehandler)

##----------status----------------------------------------
STATUS_UNKNOWN=3
STATUS_CRITICAL=2
STATUS_WARNING=1
STATUS_OK=0
MSG_HEASTATUS=["OK","WARNING","CRITICAL","UNKNOWN"]


##-------------- OID---------------------------------------
OID_SYSTEM_STATUS ="1.3.6.1.4.1.2011.2.82.1.82.1.1.0"
OID_SHELF_STATUS  ="1.3.6.1.4.1.2011.2.82.1.82.2.5.0"
OID_SMM_STATUS    ="1.3.6.1.4.1.2011.2.82.1.82.3.9.0"
#'''upload need BULK '''
OID_FAN_STATUS    ="1.3.6.1.4.1.2011.2.82.1.82.5.2001.1.7" 
OID_FAN_PRESENCE  ="1.3.6.1.4.1.2011.2.82.1.82.5.2001.1.2" 
OID_POWER_PRESENCE="1.3.6.1.4.1.2011.2.82.1.82.6.2001.1.2"
OID_POWER_STATUS  ="1.3.6.1.4.1.2011.2.82.1.82.6.2001.1.3"
#''' OID NEED HANDLE SPECIALLY'''
OID_BLADE_PRESENCE="1.3.6.1.4.1.2011.2.82.1.82.4.%s.6.0"
OID_BLADE_STATUE  ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.8.0"
OID_BLADE_INFO    ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.39.0"

OID_BLADE_CPU_PRESENT    ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2006.1.4"
OID_BLADE_CPU_STATUS    ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2006.1.5"
OID_BLADE_MEMORY_PRESENT ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2007.1.4"
OID_BLADE_MEMORY_STATUS ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2007.1.5"
OID_BLADE_MEZZ_PRESENT   ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2008.1.4"
OID_BLADE_MEZZ_STATUS   ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2008.1.5"
OID_BLADE_DISK_PRESENT   ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2009.1.4"
OID_BLADE_DISK_STATUS   ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2009.1.5"
OID_BLADE_RAID_PRESENT  ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2011.1.2"
OID_BLADE_RAID_NAME  ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2011.1.3"
OID_BLADE_RAID_STATUS   ="1.3.6.1.4.1.2011.2.82.1.82.4.%s.2011.1.7"
BLADE_CPU = "CPU"
BLADE_MEMORY= "MEMORY"
BLADE_MEZZ= "MEZZ" 
BLADE_DISK= "DISK"
BLADE_RAID= "RAID"

DIS_BLADE_INFO_OID={\
   BLADE_CPU :[OID_BLADE_CPU_PRESENT,OID_BLADE_CPU_STATUS] ,\
   BLADE_MEMORY :[OID_BLADE_MEMORY_PRESENT,OID_BLADE_MEMORY_STATUS] ,\
   BLADE_MEZZ :[OID_BLADE_MEZZ_PRESENT,OID_BLADE_MEZZ_STATUS] ,\
   BLADE_DISK :[OID_BLADE_DISK_PRESENT,OID_BLADE_DISK_STATUS] ,\
   BLADE_RAID :[OID_BLADE_RAID_PRESENT,OID_BLADE_RAID_STATUS] ,\
}

OID_SWI_PRESENCE         ="1.3.6.1.4.1.2011.2.82.1.82.7.%s.6.0"
OID_SWI_STATUS         ="1.3.6.1.4.1.2011.2.82.1.82.7.%s.8.0"

##---------------------------compoNens----------------------
COMPONENT_POWER="power"
COMPONENT_BLADE="blade"
COMPONENT_FAN="fan"
COMPONENT_SYS= "system"

COMPONENT_SWI="switch"
COMPONENT_SMM="smm"
COMPONENT_SHELF="shelf"

def commandParse():
    opts={}
    parser = OptionParser()
    parser.add_option("-c","--component", dest="component", 
        help="component for check  as (power,cpu,memory,fan,system,hardDisk)",default="system")
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
        help="Timeout in seconds for SNMP", default="3") 
    parser.add_option("-r","--retry", dest="retry",
        help="retry for  SNMP", default="2")        
    (opts,args) = parser.parse_args()
    compenlist=[COMPONENT_POWER,COMPONENT_FAN,COMPONENT_SYS\
    ,COMPONENT_SWI,COMPONENT_SMM,COMPONENT_SHELF,COMPONENT_BLADE]
    
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
        
    return opts   

class InfoHandler():     
    def __init__(self , parmlist):
        self._Parm = parmlist
    def outputStatus(self):
        _status=STATUS_UNKNOWN
        _infoStr=''
        if  not self._Parm.component == None:
            _status, _infoStr=self.getAllStatus( self._Parm.component)         
        print "%s HealthStatus: %s "% ( str(self._Parm.component) ,MSG_HEASTATUS[_status])
        print "=============================== info ============================="
        print _infoStr
        return _status 
    def snmpGet(self,oid):
        ret=1
        output=""
        if self._Parm.version =='3':
            _comStr="snmpget -u %s -t %s -r %s -v %s -l %s -a %s -A %s -x %s -X %s %s:%s %s"\
                 %(self._Parm.user\
                 ,self._Parm.timeout\
                  ,self._Parm.retry\
                 ,self._Parm.version\
                 ,self._Parm.seclevel\
                 ,self._Parm.aprotocol\
                 ,self._Parm.apwd\
                 ,self._Parm.pprotocol\
                 ,self._Parm.ppwd\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)
        else :
            _comStr="snmpget  -t %s -r %s -v %s -c %s  %s:%s %s"\
                  %(
                 self._Parm.timeout\
                  ,self._Parm.retry\
                 ,self._Parm.version\
                 ,self._Parm.community\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)          
                
        ret,output = self.runCommand(_comStr) 
        return ret,output
    def snmpWalk(self,oid):
        _ret="1"
        _output=""
        if self._Parm.version =='3':
            _comStr="snmpwalk -u %s -t %s -r %s -v %s -l %s -a %s -A %s -x %s -X %s %s:%s %s"\
                  %(self._Parm.user\
                 ,self._Parm.timeout\
                  ,self._Parm.retry\
                 ,self._Parm.version\
                 ,self._Parm.seclevel\
                 ,self._Parm.aprotocol\
                 ,self._Parm.apwd\
                 ,self._Parm.pprotocol\
                 ,self._Parm.ppwd\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)
        else :
            _comStr="snmpwalk  -t %s -r %s -v %s -c %s  %s:%s %s"\
                  %(
                  self._Parm.timeout\
                 ,self._Parm.retry\
                 ,self._Parm.version\
                 ,self._Parm.community\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)           
        _ret,_output = self.runCommand(_comStr)    
        return _ret,_output
    def getAllStatus(self,component): 
        _status=STATUS_UNKNOWN  
        _info=''
        _funDis={
            COMPONENT_POWER: self.getPowerStatus ,
            COMPONENT_FAN:self.getFanStatus,
            COMPONENT_SYS:self.getSysStatus,
            COMPONENT_BLADE:self.getBladeStatus,
            COMPONENT_SWI:self.getSwiStatus,
            COMPONENT_SMM:self.getSmmStatus,   
            COMPONENT_SHELF:self.getShelfStatus                  
        }
        _status,_info=_funDis[component]()
        return _status,_info
    def getBladeStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _ret='1'
        _output=""
        _bladeNum=32
        _presentIndexList=[]
        for i in range(_bladeNum):
            _presentStatu =self.getBladepresentStatus(i+1)
            if _presentStatu == '1':
                 _presentIndexList.append(i+1)
        # only  get present  balde info
        if   _presentIndexList== [] :
            return STATUS_OK , "no blade present" 
        _status = STATUS_OK  
        statuslist = []      
        for _item in  _presentIndexList:
            _healthStatus = self.getBladeHealthStatus(_item)
            _baldecpuInfo = self.getBladeAllInfo(_item, BLADE_CPU)
            _bladeMemoryInfo = self.getBladeAllInfo(_item,BLADE_MEMORY)
            _bladeDiskInfo = self.getBladeAllInfo(_item, BLADE_DISK)
            _bladeMezzInfo= self.getBladeAllInfo(_item,BLADE_MEZZ )
            _bladeRaidInfo = self.getBladeAllInfo(_item,BLADE_RAID)             
            _info=_info + "blade "+str(_item)+":" +MSG_HEASTATUS[_healthStatus] +"\n"\
                + _baldecpuInfo + _bladeMemoryInfo\
                + _bladeDiskInfo + _bladeMezzInfo\
                + _bladeRaidInfo + "\n"
            statuslist.append(_healthStatus)
        if  statuslist ==[]:
            _status =  STATUS_UNKNOWN      
        elif  STATUS_CRITICAL in statuslist:
            _status = STATUS_CRITICAL
        elif  STATUS_WARNING in statuslist:
            _status = STATUS_WARNING
        elif STATUS_OK in statuslist:
             _status = STATUS_OK
        else: 
             _status = STATUS_UNKNOWN
        return  _status ,_info
    def getBladeAllInfo(self ,bladeNo,component):
        _info=''
        _ret='1'
        _output=""
        '''
        1 ok
        2 minor
        3 major
        4 critical
        5 unknown
        '''
        _dis={"1":"OK" ,"2":"WARING","3":"CRITICAL" ,"4":"CRITICAL"\
               ,"5":"UNKNOWN" }
        _tempListstatus=[]
        '''
        2 poweroff
        1 prsent
        0 offline
        
        '''
        _tempListpresent=[]
        _ret,_output = self.snmpWalk(DIS_BLADE_INFO_OID[component][1]%str(bladeNo))
       
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListstatus .append(matcher.group(1).strip()) 

        _ret,_output = self.snmpWalk(DIS_BLADE_INFO_OID[component][0]%str(bladeNo))
        
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListpresent .append(matcher.group(1).strip()) 
         
        if   _tempListstatus ==[] or _tempListpresent == []:
            print  " get blade %s status and present  error    "%component
            return  "get %s info error" %component
        
        _totalcnt = len(_tempListpresent)  
        _presentIndexList = [] 
     
        for i in range(_totalcnt):
            # find  presented 
            if  self.checkBladeComponentPresen(_tempListpresent[i],component) :
                 _presentIndexList.append(i)
        _presentMessage=("%s presentStatus:"%component) + str(len(_presentIndexList))+'/'+str(_totalcnt)+"\n"
        _satatusMesssage=''        
        for _item in _presentIndexList:
            _satatusMesssage = _satatusMesssage +("%s"%component)+str(_item)+ " status: " \
                 + self.replacebaldeStatu(_tempListstatus[_item],component) + '; '
            
        _info=_presentMessage +_satatusMesssage +'\n' 
        return   _info
    def checkBladeComponentPresen(self, presentStatus,component ):
        # raid  presense status is not as others
        if component.upper() == BLADE_RAID:
            if presentStatus == "2":
                return False
            else:
                return True    
        else :
            if presentStatus == "0":
                return False
            else :
                return True      
    def replacebaldeStatu(self,status,component):
        '''
        1 ok
        2 minor
        3 major
        4 critical
        5 unknown
        '''
        if component =="RAID":
            if  status=="-1":
                return "UNKNOWN" 
            elif status =="1":
                return "ok"   
            else :
                return "WARNING"        

        _dis={"1":"OK" ,"2":"WARING","3":"CRITICAL" ,"4":"CRITICAL","5":"UNKNOWN" }
        if status in _dis.keys():
            return  _dis[status]
        else :
            return "UNKNOWN"             
    def getBladeHealthStatus(self, bladeNo ):
        _ret='1'
        _output=""
        _ret,_output = self.snmpGet(OID_BLADE_STATUE%str(bladeNo)) 
           
        if _ret == '0':
            matcher=re.match( ".*=.*:(.*)", _output) 
            if not matcher == None:
                return self.replaceStatus(matcher.group(1).strip() ) 
        return STATUS_UNKNOWN    
    def getBladepresentStatus(self, bladeNo ):
        _ret='1'
        _output=""
        _ret,_output = self.snmpGet(OID_BLADE_PRESENCE%str(bladeNo))        
        if _ret == '0':
            matcher=re.match( ".*=.*:(.*)", _output) 
            if not matcher == None:
                return (matcher.group(1).strip() )
        return None

    def getPowerStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _ret='1'
        _output=""
        '''
        0 health
        1 critical
        
        '''
        _dis={"0":"OK" ,"1":"CRITICAL"  }
        _tempListstatus=[]
        '''
        1 prsent
        0 offline
        '''
        _tempListpresent=[]
        _ret,_output = self.snmpWalk(OID_POWER_STATUS)
       
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListstatus .append(matcher.group(1).strip()) 

        _ret,_output = self.snmpWalk(OID_POWER_PRESENCE)
        
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListpresent .append(matcher.group(1).strip()) 
        if   _tempListstatus ==[] or _tempListpresent == []:
            print  " get power status and present  error    "
            return   _status ,_info 
        _totalcnt = len(_tempListpresent)  
        _presentIndexList = []                         
        for i in range(_totalcnt):
            # find  presented  power 
            if _tempListpresent[i] == "1":
                 _presentIndexList.append(i)
        _presentMessage="presentStatus:"+ str(len(_presentIndexList))+'/'+str(_totalcnt)+"\n"
        _satatusMesssage=''
        _status = STATUS_OK
        for _item in _presentIndexList:
            _satatusMesssage = _satatusMesssage +'power'+str(_item)+ " status: " \
                 + _dis[_tempListstatus[_item]] + '; '
            if "1" == _tempListstatus[_item]:
                _status =  STATUS_CRITICAL  
        _info=_presentMessage +_satatusMesssage +'\n' 
        return  _status ,_info
  
    def getFanStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _ret='1'
        _output=""
       
        '''
        1 health
        2 critical
        3 unknown
        '''
        _dis={"1":"OK" ,"2":"CRITICAL","5":"UNKNOWN"  }
        _tempListstatus=[]
        '''
        1 prsent
        0 offline
        '''
        _tempListpresent=[]
        _ret,_output = self.snmpWalk(OID_FAN_STATUS)
        
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListstatus .append(matcher.group(1).strip()) 
        _ret,_output = self.snmpWalk(OID_FAN_PRESENCE)
        
        if _ret == '0':
            tmplist=_output.split("\n")
            for itemTmp in tmplist: 
                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                if not matcher == None:
                     _tempListpresent .append(matcher.group(1).strip()) 
        if   _tempListstatus ==[] or _tempListpresent == []:
            print  " get fan status and present  error    "
            return   _status ,_info 
        _totalcnt = len(_tempListpresent)  
        _presentIndexList = []                         
        for i in range(_totalcnt):
            # find  presented  fan 
            if _tempListpresent[i] == "1":
                 _presentIndexList.append(i)
        _presentMessage="presentStatus:"+ str(len(_presentIndexList))+'/'+str(_totalcnt)+"\n"
        _satatusMesssage=''
        _status = STATUS_OK
        for _item in _presentIndexList:
            _satatusMesssage = _satatusMesssage +'fan'+str(_item)+ " status: " \
                 + _dis[_tempListstatus[_item]] + '; '
            if "2" == _tempListstatus[_item]:
                _status =  STATUS_CRITICAL  
            if "5" ==   _tempListstatus[_item] and (not (_status ==STATUS_CRITICAL ) ): 
                _status =  STATUS_WARNING     
        _info=_presentMessage +_satatusMesssage +'\n' 
        return  _status ,_info 
    def getSysStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _status=self.getcommonStatus(OID_SYSTEM_STATUS)  
        return  _status ,_info  
    def getcommonStatus(self,oid):
        _status= STATUS_UNKNOWN
        _ret='1'
        _output=""
        _ret,_output = self.snmpGet(oid)
        if _ret == "0":
            matcher=re.match( ".*=.*:(.*)", _output)
            if  not matcher is None: 
                 _tmpStatu = matcher.group(1).strip()
            _status = self.replaceStatus(_tmpStatu)
        return _status
    def replaceStatus(self,statusin) :
        _status=STATUS_UNKNOWN
        _dis={'0':STATUS_OK,'1':STATUS_WARNING,'2':STATUS_CRITICAL,\
        '3':STATUS_CRITICAL,'4':STATUS_CRITICAL,'5':STATUS_CRITICAL,\
        '6':STATUS_CRITICAL,'7':STATUS_CRITICAL}
        if statusin not in _dis.keys():
            return  STATUS_UNKNOWN
        _status=_dis[statusin] 
        return  _status
  
    def getSwiStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _ret='1'
        _output=""
        _bladeNum=4
        _presentIndexList=[]
        for i in range(_bladeNum):
            _presentStatu =self.getSwiPresentStatus(i+1)
            if _presentStatu == '1':
                 _presentIndexList.append(i+1)
        # only  get present  balde info
        if   _presentIndexList== [] :
            return STATUS_UNKNOWN , "no switch present"
        _status = STATUS_OK  
        statuslist=[]   
        for swiNo in _presentIndexList:
            _ret,_output = self.snmpGet(OID_SWI_STATUS%str(swiNo))
            _tmpstatus =  STATUS_UNKNOWN    
            if _ret == '0':
                matcher=re.match( ".*=.*:(.*)", _output) 
                if not matcher == None:
                     _tmpstatus=self.replaceStatus( matcher.group(1).strip() ) 
            statuslist.append(_tmpstatus)
            _info=_info+ "switch" +str(swiNo) +" status:" +MSG_HEASTATUS[_tmpstatus]+"; "  
            
        if  statuslist ==[]:
            _status =  STATUS_UNKNOWN      
        elif  STATUS_CRITICAL in statuslist:
            _status = STATUS_CRITICAL
        elif  STATUS_WARNING in statuslist: 
            _status = STATUS_WARNING
        elif STATUS_OK in statuslist: 
             _status = STATUS_OK
        else:
             _status = STATUS_UNKNOWN
        return  _status,_info 

    def getSwiPresentStatus(self,swiNo):
        _ret='1'
        _output=""
        _ret,_output = self.snmpGet(OID_SWI_PRESENCE%str(swiNo))        
        if _ret == '0':
            matcher=re.match( ".*=.*:(.*)", _output) 
            if not matcher == None:
                return (matcher.group(1).strip() )
        return None
          
    def getSmmStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _status=self.getcommonStatus(OID_SMM_STATUS)
        return  _status,_info
    def getShelfStatus(self):
        _status=STATUS_UNKNOWN
        _info=''
        _status=self.getcommonStatus(OID_SHELF_STATUS)
        return  _status ,_info                               
    
    def runCommand(self,command):
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,)
        stdout, stderr = proc.communicate('through stdin to stdout')
        if not proc.returncode == 0:
            logger.error("Error %s: %s\n " % (proc.returncode,stderr.strip()))
            if proc.returncode == 127: # File not found, lets print path
                path=getenv("PATH")
                logger.error( "cmdout:",stdout)
                logger.error("Check if your path is correct %s" % (path) )
        return str(proc.returncode),stdout    
    
if __name__ == '__main__':    
    try:
        commandDic=None
        commandDic=commandParse()
        infoHandler =InfoHandler(commandDic)
        state = infoHandler.outputStatus()
        exit(state)
    except Exception, e:
        print "Unhandled exception while running script: %s" % e
        exit(STATUS_UNKNOWN)