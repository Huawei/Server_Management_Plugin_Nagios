#!/usr/bin/python
from optparse import OptionParser
import os
import re
import sys
import subprocess

##----------status----------------------------------------
STATUS_UNKNOWN=3
STATUS_CRITICAL=2
STATUS_WARNING=1
STATUS_OK=0
MSG_HEASTATUS=["OK","WARNING","CRITICAL","UNKNOWN"]


##--------------OID---------------------------------------
OID_LIST_SYSTEM=[ {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.1.0" ,"replace":"1:0,2:1,3:1,4:2"},\
                  {"status":"off", "method":"bulk","name":"alarmstatus","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.50.1.4" ,"replace":"1:0,2:1,3:1,4:2"},\
                  {"status":"off", "method":"bulk","name":"alarmsdecription","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.50.1.5"},\
                  {"status":"off", "method":"get", "name":"deviceName","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.6.0"},\
                  {"status":"off", "method":"get", "name":"deviceSerialNo","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.7.0"},\
                  {"status":"off", "method":"get", "name":"systemPowerState","oid":"1.3.6.1.4.1.2011.2.235.1.1.1.12.0","replace":\
                  "1:gracefulPowerOff,2:powerOn,3:coldReset,4:gracefulReboot,5:forciblyPowerOff"}] 
OID_LIST_CPU=[  {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.15.1.0" ,"replace":"1:0,2:1,3:1,4:2,5:3,6:3"},\
                {"status":"off", "method":"bulk", "name":"presence","oid":"1.3.6.1.4.1.2011.2.235.1.1.15.50.1.6","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"},\
                {"status":"off", "method":"bulk", "name":"devicename","oid":"1.3.6.1.4.1.2011.2.235.1.1.15.50.1.10"},\
                {"status":"off", "method":"bulk", "name":"state","oid":"1.3.6.1.4.1.2011.2.235.1.1.15.50.1.6","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"} ]
OID_LIST_FAN=[  {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.8.3.0" ,"replace":"1:0,2:1,3:1,4:2,5:3,6:3"},\
                {"status":"off", "method":"bulk", "name":"presence","oid":"1.3.6.1.4.1.2011.2.235.1.1.8.50.1.3","replace":"1:absence,2:presence,3:unknown"},\
                {"status":"off", "method":"bulk", "name":"devicename","oid":"1.3.6.1.4.1.2011.2.235.1.1.8.50.1.7"},\
                {"status":"off", "method":"bulk", "name":"state","oid":"1.3.6.1.4.1.2011.2.235.1.1.8.50.1.4","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"} ]
OID_LIST_POWER=[  {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.6.1.0" ,"replace":"1:0,2:1,3:1,4:2,5:3,6:3"},\
                {"status":"off", "method":"bulk", "name":"presence","oid":"1.3.6.1.4.1.2011.2.235.1.1.6.50.1.9","replace":"1:absence,2:presence,3:unknown"},\
                {"status":"off", "method":"bulk", "name":"devicename","oid":"1.3.6.1.4.1.2011.2.235.1.1.6.50.1.13"},\
                {"status":"off", "method":"bulk", "name":"state","oid":"1.3.6.1.4.1.2011.2.235.1.1.6.50.1.7","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"} ]
OID_LIST_DISK=[  {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.18.1.0" ,"replace":"1:0,2:1,3:1,4:2,5:3,6:3"},\
                {"status":"off", "method":"bulk", "name":"presence","oid":"1.3.6.1.4.1.2011.2.235.1.1.18.50.1.2","replace":"1:absence,2:presence,3:unknown"},\
                {"status":"off", "method":"bulk", "name":"devicename","oid":"1.3.6.1.4.1.2011.2.235.1.1.18.50.1.6"},\
                {"status":"off", "method":"bulk", "name":"state","oid":"1.3.6.1.4.1.2011.2.235.1.1.18.50.1.3","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"} ]
OID_LIST_MEN=[  {"status":"on", "method":"get","oid":"1.3.6.1.4.1.2011.2.235.1.1.16.1.0" ,"replace":"1:0,2:1,3:1,4:2,5:3,6:3"},\
                {"status":"off", "method":"bulk", "name":"presence","oid":"1.3.6.1.4.1.2011.2.235.1.1.16.50.1.6","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"},\
                {"status":"off", "method":"bulk", "name":"devicename","oid":"1.3.6.1.4.1.2011.2.235.1.1.16.50.1.10"},\
                {"status":"off", "method":"bulk", "name":"state","oid":"1.3.6.1.4.1.2011.2.235.1.1.16.50.1.6","replace":"1:ok,2:minor,3:major,4:critical,5:absence,6:unknown"} ]
               
OID_DIC={ "power":OID_LIST_POWER,\
           "cpu" :OID_LIST_CPU,\
           "memory":OID_LIST_MEN,\
           "fan":OID_LIST_FAN,\
           "hardDisk":OID_LIST_DISK,\
           "system":OID_LIST_SYSTEM }                  
                  
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
        help="Timeout in seconds for SNMP", default="10")
    (opts,args) = parser.parse_args()
    compenlist=["power","cpu","memory","fan","system","hardDisk"]
    
    if  opts.host== None :
        print  "please input Hostname or IP "
        exit(STATUS_UNKNOWN)
    if  opts.user== None :
        print  "please input SNMP username  "
        exit(STATUS_UNKNOWN)  
    if  opts.ppwd== None :
        opts.ppwd = opts.apwd  
    if not opts.component in compenlist:
       print  " -c  conly support as : power,cpu,memory,fan,system,hardDisk "  
       exit(STATUS_UNKNOWN)
    return opts    
    

class InfoHandler():
    def __init__(self , parmlist):
        self._Parm = parmlist
    def getStatu(self):
        _statu=STATUS_UNKNOWN
        _infoStr=''
        if  not self._Parm.component == None:
             _statu=self.getStatuOid( self._Parm.component)
        else:
            print "error getStatuOid input None " 
        if  not self._Parm.component == None:
             _infoStr=self.getMessageOid(  self._Parm.component)
        else:
            print "error getMessageOid input None "             
        print "=============Result============="
        print "%s:"%self._Parm.component,_infoStr
        print "HealthStatus:%s"%MSG_HEASTATUS[_statu]
        return _statu 
    def snmpGet(self,oid):
        ret=1
        output=""
        _comStr="snmpget -u %s -t %s -r 0 -v %s -l %s -a %s -A %s -x %s -X %s %s:%s %s"\
                 %(self._Parm.user\
                 ,self._Parm.timeout\
                 ,self._Parm.version\
                 ,self._Parm.seclevel\
                 ,self._Parm.aprotocol\
                 ,self._Parm.apwd\
                 ,self._Parm.pprotocol\
                 ,self._Parm.ppwd\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)
        ret,output = self.runCommand(_comStr) 
        return ret,output
    def snmpWalk(self,oid):
        _ret="1"
        _output=""
        _comStr="snmpwalk -u %s -t %s -r 0 -v %s -l %s -a %s -A %s -x %s -X %s %s:%s %s"\
                  %(self._Parm.user\
                 ,self._Parm.timeout\
                 ,self._Parm.version\
                 ,self._Parm.seclevel\
                 ,self._Parm.aprotocol\
                 ,self._Parm.apwd\
                 ,self._Parm.pprotocol\
                 ,self._Parm.ppwd\
                 ,self._Parm.host\
                 ,self._Parm.port\
                 ,oid)
        _ret,_output = self.runCommand(_comStr)    
        return _ret,_output
    def _repalce(self ,strSrc,repleaseStr):
        _ret = STATUS_UNKNOWN
        strlist= repleaseStr.strip().split(",") 
        for strRe in strlist:
            if strSrc == strRe.split(":")[0]:
                _ret = strRe.split(":")[1] 
        return _ret
        
    def getStatuOid(self,component): 
        _statu=STATUS_UNKNOWN  
        _ret="1"
        _output=""
        oidlist = OID_DIC[component]
        for oidDis in oidlist:
            if oidDis[ "status" ] == "on" and \
                oidDis[ "method"] == "get":
                _ret,_ouput=self.snmpGet(oidDis["oid"])
                if _ret == "0":
                    if "replace" in oidDis.keys():
                        matcher=re.match( ".*=.*:(.*)", _ouput)
                        if  not matcher == None: 
                            _tmpStatu = matcher.group(1).strip()                      
                            _statu=int(self._repalce(_tmpStatu,oidDis["replace"]))
                else: 
                    print "snmpget  end with error "
        return _statu
    def getMessageOid(self,component): 
        _infoStr=""
        _ret="1"
        _output=""
        oidlist = OID_DIC[component]
        presentStatuList=[]
        nameList=[]
        StatusList=[]
        AlarmStatus=[]
        AlarmDecrition=[]
        for oidDis in oidlist:
            if oidDis[ "status" ] == "off":
                
                if oidDis[ "method"] == "get":
                    _ret,_ouput=self.snmpGet(oidDis["oid"])
                    if _ret=="0":
                        matcher=re.match( ".*=.*:(.*)", _ouput)
                        if  not matcher == None: 
                            if "replace" in oidDis.keys():
                                _infoStr = _infoStr + oidDis[ "name"] + \
                                    self._repalce( matcher.group(1).strip(), oidDis["replace"])
                            else:
                                _infoStr = _infoStr +oidDis[ "name"] + " "+matcher.group(1)+" "
                    else:
                        print "snmpget  end with error "                   
                elif oidDis[ "method"] == "bulk": 
                    _ret,_ouput=self.snmpWalk(oidDis["oid"])
                    if _ret=="0":
                        tmpList=_ouput.split("\n")
                        if  oidDis[ "name"] == "presence": 
                            for itemTmp in tmpList:
                                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                                if not matcher == None:
                                    presentStatuList.append( \
                                      self._repalce( matcher.group(1).strip(), oidDis["replace"]))
                        elif oidDis[ "name"] == "devicename": 
                            for itemTmp in tmpList:
                                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                                if not matcher == None:
                                    nameList.append(matcher.group(1).strip()) 
                        elif oidDis["name"] == "state":             
                            for itemTmp in tmpList:
                                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                                if not matcher == None:
                                    StatusList.append( \
                                       self._repalce(  matcher.group(1).strip(),oidDis["replace"] ))
                        elif oidDis[ "name"] == "alarmstatus": 
                            for itemTmp in tmpList:
                                matcher=re.match( ".*=.*:(.*)", itemTmp) 
                                if not matcher == None:
                                    AlarmStatus.append( \
                                      self._repalce( matcher.group(1).strip(), oidDis["replace"]))  
                        elif oidDis[ "name"] == "alarmsdecription":                        
                            for itemTmp in tmpList:
                                matcher=re.match( ".*=.*:.*\"(.*)\"", itemTmp) 
                                if not matcher == None:
                                    AlarmDecrition.append( matcher.group(1))
                        else:
                            print "oidDis[ name], config error :",oidDis[ "name"]                         
                    else:
                        print "snmpwalk end with error ",oidDis["name"]
                else:
                    print "oidDis[ method] config error :", oidDis[ "method"]           
        _alldevice=len( presentStatuList)        
        if  _alldevice >= 1:
            presentCnt=0
            for i in range(_alldevice):
                if not "absence" == presentStatuList[i]:
                    presentCnt=presentCnt+1
                    _infoStr=_infoStr+str(presentCnt)+":"+nameList[presentCnt-1]+" "+ "status: " + StatusList[i] +"\n"
            presentMsg=" presentStatus:"+str(presentCnt)+"/"+ str(_alldevice)+"\n"
            _infoStr = presentMsg + _infoStr
        _allAlarm=len( AlarmStatus ) 
        if  _allAlarm >=1 :
            _infoStr=_infoStr + "\n \n============== alarms =================\n"
            cnt=0 
            for i in range(_allAlarm):
                cnt=cnt + 1 
                _infoStr= _infoStr + str(cnt) + "," + AlarmDecrition[i] + " status:"+ MSG_HEASTATUS[int(AlarmStatus[i])]+"\n"
        return _infoStr  
    def runCommand(self,command):
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,)
        stdout, stderr = proc.communicate('through stdin to stdout')
        if not proc.returncode == 0:
            print "Error %s: %s\n " % (proc.returncode,stderr.strip())
            if proc.returncode == 127: # File not found, lets print path
                path=getenv("PATH")
                print "cmdout:",stdout
                print "Check if your path is correct %s" % (path) 
      
        return str(proc.returncode),stdout       

if __name__ == '__main__':
    try:
        commandDic=None
        commandDic=commandParse()
        infoHandler =InfoHandler(commandDic)
        state = infoHandler.getStatu()
        exit(state)
    except Exception, e:
        print "Unhandled exception while running script: %s" % e
        exit(STATUS_UNKNOWN)
	