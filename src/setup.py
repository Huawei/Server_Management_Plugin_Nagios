#coding=utf-8
'''
Created on 2013-3-26

'''
from optparse import OptionParser
import glob
import inspect
import os
import re
import shutil
import sys
import commands

G_CMK_USER='prod'
G_CMK_GROUP='prod'
G_NAGIOS_USER='nagios'
G_NAGIOS_GROUP='nagios'
this_file = inspect.getfile(inspect.currentframe())
file_dir, file_name = os.path.split(this_file)
if file_dir == '' :
    file_dir = os.getcwd()
usrFile=file_dir+os.path.sep+'usrFile.cfg'

def getUsrInfo():
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
        if re.findall(r'usr.*=.*', eachline):
            usr = eachline.split('=')[1]
        if re.findall(r'group.*=.*', eachline):  
            group =eachline.split('=')[1]   
    return usr.strip(),group.strip()

def getNagiosUserinfo():
    list = commands.getoutput( "ls -l /usr/local/nagios ")
    infolist = list.split('\n')[1].split()
    usr= infolist[2]
    group=infolist[3]
    return usr, group 
        

'''
==================================
日志
==================================
'''

##兼容的check mk 版本
CHECK_MK_VERSION_LIST=["1_2","1_5","1_4"]


class Log:
    '''
    '日志级别：warn，info, debug
    '''
    __logContainer = {'error':3, 'info':2, 'debug':1}
    __classname = ''
    
    '''
    '日志数据保存路径
    '''
    __logfilepath = ''
    
    def __init__(self, classname=None): 
        if classname is not None:
            self.__classname = str(classname) + '=> ' 
    def error(self, textContent=''):
        if 4 > self.__logContainer[TargetPath.LOG_LEVEL] :
            print self.__classname, '[error]', textContent
    def info(self, textContent=''):
        if 3 > self.__logContainer[TargetPath.LOG_LEVEL] :
            print self.__classname, '[info]', textContent
    def debug(self, textContent=''):
        if 2 > self.__logContainer[TargetPath.LOG_LEVEL] :
            print self.__classname, '[debug]', textContent


'''
'==================================
'进行配置
'==================================
'''
class CheckCfgTask:
    LOG = Log('check_cfg_task.py')
    '''
    '配置路径    
    '''   
    def checkPath(self, pathStr):   
        result = self.isDir(pathStr) or self.isFile(pathStr) or self.isExists(pathStr)
        if not result:
            self.LOG.error('checkpath:' + pathStr + (result and '  sucess.' or '  fail.')) 
        return result
    
    def checkPathNot(self, pathStr):   
        result = self.isDir(pathStr) or self.isFile(pathStr) or self.isExists(pathStr)
        if result :
            self.LOG.error('checkpath:' + pathStr + (result and '  fail.' or '  sucess.')) 
        return result
    
    '''
    '判断是否为文件
    '''
    def isFile(self, pathStr):
        if os.path.isfile(pathStr):
            return True
        else:
            return False
        
    '''
    ‘判断是否为目录
    '''
    def isDir(self, pathStr):
        if os.path.isdir(pathStr):
            return True
        else:
            return False
    
    '''
    ‘判断路径存在
    '''
    def isExists(self, pathStr):
        if os.path.exists(pathStr):
            return True
        else:
            return False
        
    '''
    '判断是否编辑
    '''
    def isWrite(self, pathStr):
        try:
            f = None
            try:
                f = open(pathStr, "a+")
                f.write('')
            except:
                self.LOG.info('check:' + pathStr + ' fail.') 
                return False
            else: 
                return True
        finally:
           if f is not None:
                f.close()
        
    '''
    '配置是否有误
    '''
    def checkNagiosCfg(self, command):
        return os.system(command)


#store ckMKVersion 
class CKmkVersion():
    __ckmkVersion = '' 

    @classmethod     
    def setckmkVersion(cls,version):
        cls.__ckmkVersion = version
    @classmethod     
    def getckmkVersion(cls): 
        return cls.__ckmkVersion
    @classmethod    
    def find_ckmkVersion(cls):
        '''return nagios directory'''
        cmd = "source /etc/profile;echo $NAGIOS_CHECKMK_VERSION"
        procs = commands.getoutput(cmd)
        return procs  
def find_nagiosdir():
        '''return nagios directory'''
        cmd = "source /etc/profile;echo $NAGIOSHOME"
        procs = commands.getoutput(cmd)
        return procs 
         
def delckmkVersionToprofile(): 
    FilePath="/etc/profile"
    strforconfig="export NAGIOS_CHECKMK_VERSION"
    file=None
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()
        file.close()    
        #had configed so exit          
        for i in range(len(strlist)):
            if strforconfig in str(strlist[i]):
                del strlist[i]
                break 
        #cofnig   nagios.cfg 
        file=open(FilePath,"w")       
        file.writelines(strlist)  
    except Exception,err:
        print  "delNagiosHomeToprofile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()      
def addckmkVersionToprofile():
    FilePath="/etc/profile"
    strforconfig="export NAGIOS_CHECKMK_VERSION="
    file=None
    delckmkVersionToprofile()
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()  
        file.writelines(strforconfig+( "%s"% CKmkVersion.getckmkVersion() ) +"\n") 
        
    except Exception,err:
        print  "addckmkVersionToprofile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close() 

'''
'==================================
'查找匹配移动文件
'==================================
'''
class FileMrg:
    LOG = Log('file_mrg.py')
    '''
    '读取文件
    'regFindContent  选择插入的位置
    'regPtContent    完全匹配textContent
    '''
    def readEditFile(self, nagiosCfgPath, textContent, regIndexContent=None, regPtContent=None, mode=True):
        '''
        '如果更改的文件内容不是一个路径
        '''
        if not os.path.isfile(nagiosCfgPath) :
            return
        
        nagiosCfgPathBak = nagiosCfgPath + '.bak'
        insertContent = textContent
        
        if None == regIndexContent:
            regIndexContent = r'^\s*' + insertContent
        if None == regPtContent:
            regPtContent = r'^\s*' + insertContent + r'\s*$'
        patt = re.compile(regIndexContent);
        patt2 = re.compile(regPtContent);
        
        runing = True
        cfgCheck = True
        
        try:
            try:
                f2 = None
                f = None
                f2 = file(nagiosCfgPathBak, 'w')
                f = file(nagiosCfgPath, 'r')
                while runing :
                    fContent = f.readline()
                    if len(fContent) == 0:
                        break
                    
                    if cfgCheck and self.contentPattern(patt, fContent) :
                        cfgCheck = False
                        if  not mode and self.contentPattern(patt2, fContent):
                            continue
                        f2.write(insertContent + "\n")
                        
                    if self.contentPattern(patt2, fContent) :
                        continue
                    
                    f2.write(fContent)
            except IOError:
                self.LOG.error('"readEditFile" Except! Permission denied.')
                return False
            else:
                self.LOG.debug('"readEditFile" update file content:' + str(nagiosCfgPath))
        finally:
            if f is not None:
                f.close()
            if f2 is not None:
              f2.close()
           
            
        result = self.withFileContent(nagiosCfgPathBak, nagiosCfgPath)
        self.removeFile(nagiosCfgPathBak)
        return result
        
    '''
    '使用文件替换另一文件
    '''
    def withFileContent(self, source, target):
        try:
            try:
                f2 = None 
                f = None 
                f2 = file(target, 'w')
                f = file(source, 'r')
                f2.write(f.read())
            except IOError:
                self.LOG.error('"withFileContent" Except! Permission denied.')
                return False
            else:
                self.LOG.debug('"withFileContent" withFileContent: success.')
                return True
        finally:
            f2.close()
            f.close()

    '''
    '移动文件
    '''
    def copyFile(self, filesouce, filetarget):   
        if os.path.isfile(filesouce) and self.excludeFile(filetarget+os.path.sep+os.path.basename(filesouce)):
            shutil.copy2(filesouce , os.path.join(filetarget))
        elif os.path.isdir(filesouce):
            dirname = os.path.basename(filesouce)
            if not os.path.isdir(os.path.join(filetarget) + os.path.sep + dirname):
                os.mkdir(os.path.join(filetarget) + os.path.sep + dirname)
            for infile in glob.glob(os.path.join(filesouce, "*")):
                self.copyFile(infile, os.path.join(filetarget) + os.path.sep + dirname)
            
    def excludeFile(self, filetarget):
        if(os.path.isfile(filetarget)):
            return False
        return True
    '''
    '移除文件
    '''
    def removeFile(self, filepath, excludeReg = None):
        filepath = os.path.join(filepath)
        if  excludeReg != None and re.findall(excludeReg, filepath):
            return;
        if os.path.isfile(filepath) :
            os.remove(filepath)
        elif os.path.isdir(filepath):
            if len(os.listdir(filepath)) != 0:
                for infile in glob.glob(os.path.join(filepath, "*")):
                    self.removeFile(infile,excludeReg)
            try:
                os.rmdir(filepath)
            except OSError:
                pass
        
    '''
    '写文件
    '''
    def createFile(self, filepath, filename, textContent, mode='w'):
        if os.path.isdir(filepath) :
            try:
                try:
                    f = None 
                    f = file(filepath + os.path.sep + filename, mode)
                    f.write(textContent)
                    f.flush()
                except IOError:
                    self.LOG.error('"createFile" Except! Permission denied.')
                    return False
                else:
                    return True
            finally:
                if f is not None:
                    f.close()
    '''
    '内容匹配
    '''
    def contentPattern(self, reg, content):
        if reg.search(content):
            return True
        return False




'''
'==================================
'配置信息
'==================================    
'''

class TargetPath(object):
    
    '''
    '当前系统的nagios_home路径
    '''
    NAGIOS_HOME = '/usr/local/nagios'

    '''
    '配置etc目录
    '''
    def nagios_etc(self):
        return '%s/etc' % self.NAGIOS_HOME
    
    '''
    '配置libexec目录
    '''
    def nagios_libexec(self):
        return '%s/libexec' % self.NAGIOS_HOME

    '''
    '配置bin目录
    '''
    def nagios_bin(self):
        return '%s/bin' % self.NAGIOS_HOME
    
    '''
    '配置nagios.config文件
    '''
    def nagios_f_config(self):
        return '%s/nagios.cfg' % self.nagios_etc()
    
    '''
    '配置cgi.config文件
    '''
    def nagios_cgi_config(self):
        return '%s/cgi.cfg' % self.nagios_etc()
    
    '''
    '当前nagios运行文件位置
    '''
    def nagios_server(self):
        return '%s/nagios' % self.nagios_bin()
    
    '''
    'nagios可执行文件目录 
    'update 2013-4-8
    '''
    def nagios_var(self):
        return '%s/var' % self.NAGIOS_HOME
    
    '''
    'nagios数据文件
    'update 2013-4-8
    '''
    NAGIOS_CMD = ''

    def nagios_cmd(self):
        if CKmkVersion.getckmkVersion() == '1_4'or CKmkVersion.getckmkVersion() == '1_5':
            return "/omd/sites/%s/tmp/run/nagios.cmd"%G_CMK_USER
        return self.NAGIOS_CMD or '%s/rw/nagios.cmd' % self.nagios_var()
    '''
    'nagios缓存目录
    'update 2013-4-8
    '''
    NAGIOS_CACHE_PATH = ''


    def nagios_cache_path(self):
        return self.NAGIOS_CACHE_PATH or '%s/huawei_server' % self.nagios_var()
    
    '''
    'nagios端口号
    'update 2013-4-8
    '''
    NAGIOS_LISTEN_PORT = 10061
    
    '''
    'nagios本机地址
    'update 2013-4-8
    '''
    NAGIOS_LOCAL_ADDRESS = '127.0.0.1'
    
    '''
    '当前模板位置
    '''
    def nagios_hw_config(self):
        return '%s/huawei_server/templates/hw_server.cfg.template' % self.nagios_etc()
    def nagios_hw_command(self):
        return '%s/huawei_server/templates/hw_command.cfg.template' % self.nagios_etc()
    def nagios_hw_ser_cfg(self):
        return '%s/huawei_server/hw_server.cfg' % self.nagios_etc()
    def nagios_hw_listener(self):
        return '%s/huawei_server/huawei_listener.cfg' % self.nagios_etc()
    
    '''
    '当前文件路径
    '''
    CURR_PATH = file_dir
    
    '''
    '日志级别
    ' error   错误
    ' info    信息
    ' debug   调试
    '''
    LOG_LEVEL = 'info'
    

class InstallExcept(Exception):
    pass
class HelpExcept(Exception):
    pass

'''
'初始化用户配置
'''
class InitUserCfg(object):
    def initHwServer(self):
        initHwSer = '''<?xml version="1.0" encoding="UTF-8"?>
<hosts>
        <host>
        <!--HOST基本信息(设备型号：Rack/HighDensity/E9000)-->
        <device>
            <hostname></hostname>
            <ipaddress></ipaddress>
            <devicetype></devicetype>
            <port>161</port>
            <user></user>
            <pass></pass>
            <authprotocol></authprotocol>
            <privprotocol></privprotocol>
        </device>
        <!--设备数据采集协议：
            1、采集数据的SNMP版本为V3，则告警上报支持V1/V2/V3；
            2、采集数据的SNMP版本为V1/V2，则告警上报只支持V1/V2
            3、E9000采集数据只支持SNMP V3版本
        -->
        <collect>
            <snmpversion></snmpversion>
            <community></community>            
        </collect>
        
        <!--设备告警上报的协议信息：
            1、E9000告警上报只支持SNMP V1/V2版本。-->
        <alarm>
            <trapsnmpversion></trapsnmpversion>
            <trapcommunity></trapcommunity>
        </alarm>
    </host>
    

</hosts>
'''
        fileMrg.createFile(targetPath.CURR_PATH + '/etc/huawei_server', 'huawei_hosts.xml', initHwSer, 'w')
    def initHuaweiHosts(self):
        fileMrg.removeFile(targetPath.CURR_PATH + '/etc/huawei_server/hw_server.cfg');
        pass
    def initCfg(self):
        self.initHwServer();
        self.initHuaweiHosts();
    pass

'''
'初始化对象
'''
targetPath = TargetPath
fileMrg = FileMrg()
checkCfgTask = CheckCfgTask()

'''
'定义变量
'''
LOG = Log('setup.py')


'''
'读取路径配置文件
'''

##如果配置文件将在这里编写


'''
'路径的正确
'''
def checkpath():
    if '1_4' in CKmkVersion.getckmkVersion() or  '1_5' in CKmkVersion.getckmkVersion():
        return True
    if(
       not checkCfgTask.checkPath(targetPath.NAGIOS_HOME)
       or not checkCfgTask.checkPath(targetPath().nagios_bin()) 
       or not checkCfgTask.checkPath(targetPath().nagios_etc()) 
       or not checkCfgTask.checkPath(targetPath().nagios_libexec()) 
       or not checkCfgTask.checkPath(targetPath().nagios_f_config()) 

       or not checkCfgTask.isWrite(targetPath().nagios_f_config()) 
       or not checkCfgTask.isWrite(targetPath().nagios_cgi_config()) 
        #更多的文件校验
        ):
        raise InstallExcept('Incorrect nagios installation path. ')
    else:
        ########
        #创建缓存目录 
        ########
        if not checkCfgTask.isDir(targetPath().nagios_cache_path()):
            os.makedirs(targetPath().nagios_cache_path(), 0775)
        return True
 

def createPluginDir():
    if not os.path.isdir (targetPath.NAGIOS_HOME):
        os.mkdir(targetPath.NAGIOS_HOME)
    if  not os.path.isdir (targetPath().nagios_etc()):
        os.mkdir(targetPath().nagios_etc())
    if  not os.path.isdir (targetPath().nagios_libexec()):
        os.mkdir(targetPath().nagios_libexec())
    if  not os.path.isdir (targetPath().nagios_bin()):
        os.mkdir(targetPath().nagios_bin())
    if  not os.path.isdir (targetPath().nagios_var()):
        os.mkdir(targetPath().nagios_var())  
    if  not os.path.isdir (targetPath().nagios_var()+"/"+"huawei_server"):
        os.mkdir(targetPath().nagios_var()+"/"+"huawei_server")      

'''
'移动python脚本至指定位
'''           
def moveFile():
    createPluginDir()
    LOG.info('moveFile begin.')
    fileMrg.copyFile(targetPath.CURR_PATH + os.path.sep + 'bin' + os.path.sep + 'huawei_server' , targetPath().nagios_bin())
    fileMrg.copyFile(targetPath.CURR_PATH + os.path.sep + 'etc' + os.path.sep + 'huawei_server' , targetPath().nagios_etc())
    fileMrg.copyFile(targetPath.CURR_PATH + os.path.sep + 'libexec' + os.path.sep + 'huawei_server' , targetPath().nagios_libexec())
    LOG.info('moveFile end.')
    
def removeFile(isSaveData):
    LOG.info('removeFile begin.')
    userData = None
    if isSaveData :
        userData = "huawei_hosts.xml|hw_server.cfg"
    fileMrg.removeFile(targetPath().nagios_bin() + os.path.sep + "huawei_server")
    fileMrg.removeFile(targetPath().nagios_etc() + os.path.sep + "huawei_server",userData)
    fileMrg.removeFile(targetPath().nagios_libexec() + os.path.sep + "huawei_server")
    fileMrg.removeFile(targetPath().nagios_cache_path())
    LOG.info('removeFile end.')
    
'''
'修改nagios配置文件 
'''
def delInfoInNagiosSourceFile(): 
    nagioshome = targetPath.NAGIOS_HOME
    if '1_4' in CKmkVersion.getckmkVersion() or  '1_5' in CKmkVersion.getckmkVersion(): 
        FilePath="/omd/sites/%s/etc/nagios/resource.cfg"%(G_CMK_USER)
    else:
        FilePath= SourceFile=nagioshome+os.path.sep +"etc"+os.path.sep+"resource.cfg"
    strforconfig="$USER5$=%s/libexec\n"%nagioshome 
    file=None
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()
        file.close()    
        #had configed so exit          
        for i in range(len(strlist)):
            if strforconfig in str(strlist[i]):
                del strlist[i]
                break 
        #cofnig   nagios.cfg 
        file=open(FilePath,"w")       
        file.writelines(strlist)  
    except Exception,err:
        print  "delInfoInNagiosSourceFile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()
def delInfoInNagiosCfg(): 
    nagioshome = targetPath.NAGIOS_HOME
    if '1_4' in CKmkVersion.getckmkVersion() or  '1_5' in CKmkVersion.getckmkVersion(): 
        FilePath="/omd/sites/%s/etc/nagios/nagios.cfg"%(G_CMK_USER)
        strforconfig="precached_object_file=%s"%nagioshome+os.path.sep+"etc"+os.path.sep+"huawei_server"+os.path.sep+"hw_server.cfg\n"
    else:
        FilePath=nagioshome+os.path.sep +"etc"+os.path.sep+"nagios.cfg"   
        strforconfig="cfg_file=%s"%nagioshome+os.path.sep+"etc"+os.path.sep+"huawei_server"+os.path.sep+"hw_server.cfg\n"
    file=None
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()
        file.close()    
        #had configed so exit          
        for i in range(len(strlist)):
            if strforconfig in str(strlist[i]):
                del strlist[i]
                break 
        #cofnig   nagios.cfg 
        file=open(FilePath,"w")       
        file.writelines(strlist)  
    except Exception,err:
        print  "delInfoInNagiosCfg exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()



def reEditFile():
    LOG.info('revert file begin.')
    
    hwCfgPt = 'cfg_file='
    hwCfg = hwCfgPt + targetPath().nagios_hw_ser_cfg()
    hwCfgPt = r'^\s*' + hwCfg + r'\s*$'
    fileMrg.readEditFile(targetPath().nagios_f_config(), hwCfg, hwCfgPt, mode=False)

    LOG.info('revert file end.')
    
'''
'配置文件正确
'''
def checkNagiosCfg():
    LOG.info('checkNagiosCfg begin.')
    command = targetPath().nagios_server() + ' -v ' + targetPath().nagios_f_config()
    checkres = checkCfgTask.checkNagiosCfg(command)
    LOG.info('checkNagiosCfg end.')
    return checkres


hw_server = 'hw_server.cfg'
hw_command = 'hw_command.cfg'
currentfilepath = os.path.abspath(os.path.dirname(this_file)) + os.path.sep + "etc" + os.path.sep + "huawei_server"


def insertInitialCfg():
    initial_content = \
'''[init]
nagios_dir=''' + targetPath.NAGIOS_HOME + '''
nagios_cmd_file=''' + targetPath().nagios_cmd() + '''
cache_path=''' + targetPath().nagios_cache_path() + '''
local_address=''' + targetPath().NAGIOS_LOCAL_ADDRESS + '''
listen_port=''' + targetPath().NAGIOS_LISTEN_PORT + '''
check_host_cmd=ping %s -c 1 > /dev/null
check_host_interval = 300.0
check_nagios_cmd=ps -efww | grep nagios | grep -v grep | awk '{print $8}' | grep %s > /dev/null
check_nagios_interval = 120.0
nagios_costant3=awei12
'''
    fileMrg.createFile(targetPath.CURR_PATH + '/etc/huawei_server', 'initial.cfg', initial_content, 'w')

    
    
#verify python vesion is 2.7.13; if yes return python executable path      
def VerifyPythonVersion():
    try:
        if str(sys.version_info[0]) == '2' and str(sys.version_info[1]) =='7' and str(sys.version_info[2])=='13':
            PythonPath=sys.executable
            print PythonPath[:-6]
            return PythonPath[:-6]
        else :
            print "check python vesion fail ,please check you python is 2.7.13" 
            exit(1)            
    except:
        print "check python vesion fail ,please check you python is 2.7.13"   
        exit(1)
        
def trapdcheck():
    PythonExcutePath=VerifyPythonVersion()
    trapdcheck= \
'''#/bin/bash

trapdNum=NULL
function getTrapdNum()
{
     trapdNum=`ps -efww | grep trapd.py|grep python | grep -v grep | awk '{print $2}'`
}

collectNum=NULL
function getCollectNum()
{
     collectNum=`ps -efww | grep collect.py|grep python | grep -v grep | awk '{print $2}'`
}
CollectbyCfgNum=NULL
function getCollectbyCfgNum()
{
     CollectbyCfgNum=`ps -efww | grep collectInfoByCfg.py|grep python | grep -v grep | awk '{print $2}'`
}

function kill()
{
    killNum=`kill -9 $1`; 
}


function startTrapd()
{

    cd `dirname $0`
    nohup python '''+targetPath().nagios_bin()+os.path.sep+'''huawei_server'''+os.path.sep+'''trapd.py > /dev/null 2>&1 &
}


function startCollect()
{

    cd `dirname $0`
    nohup python '''+targetPath().nagios_bin()+os.path.sep+'''huawei_server'''+os.path.sep+'''collect.py -p > /dev/null 2>&1 &
}

function startCollectByCfg()
{

    cd `dirname $0`
    nohup python '''+targetPath().nagios_bin()+os.path.sep+'''huawei_server'''+os.path.sep+'''collectInfoByCfg.py -p > /dev/null 2>&1 &
}



function trapdcheck()
{
    getTrapdNum
    if [ -e $trapdNum ]; then
        startTrapd
    fi
    
    getCollectNum
    if [ -e $collectNum ]; then
        startCollect
    fi
    
    getCollectbyCfgNum
    if [ -e $CollectbyCfgNum ]; then
        startCollectByCfg
    fi

    echo "OK"
    exit 0
}
source /etc/profile
export PATH="%s:$PATH"
export PYTHONPATH=''
trapdcheck
'''%PythonExcutePath
    fileMrg.createFile(targetPath.CURR_PATH + '/libexec/huawei_server', 'trapdcheck.sh', trapdcheck, 'w')
    
    # 修改启动脚本为nohup python /usr/local/nagios/bin/huawei_server/trapd.py > /dev/null &
    # 这样在trapd.py所在目录就不会出现nohup.out文件

def checkip(ip):
    if(re.findall("^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\.){3}"
            + "(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$", ip)):
        pass
    else:
        LOG.error("Incorrect IP address format.")
        raise InstallExcept()

def checkSnmpversion(snmpversion):
    if('v1' == snmpversion or 'v2c'==snmpversion or 'v3'==snmpversion):
        pass
    else:
        LOG.error("Incorrect Snmp Version format.")
        raise InstallExcept()
    
def encrypt(str):
    '''
    ' aes加密，依赖linux平台，依赖openssl
    '''
    encryptStr = os.popen("echo " +  "'" + str + "'" +  " | openssl aes-128-cbc -k '' -base64")\
                            .read().strip()
    if encryptStr is None or encryptStr == '':
        return str
    return encryptStr



def insertSerCfg():
    pass
def delNagiosHomeToprofile(): 
    FilePath="/etc/profile"
    strforconfig="export NAGIOSHOME="
    file=None
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()
        file.close()    
        #had configed so exit          
        for i in range(len(strlist)):
            if strforconfig in str(strlist[i]):
                del strlist[i]
                break 
        #cofnig   nagios.cfg 
        file=open(FilePath,"w")       
        file.writelines(strlist)  
    except Exception,err:
        print  "delNagiosHomeToprofile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()      
def addNagiosHomeToprofile():
    FilePath="/etc/profile"
    strforconfig="export NAGIOSHOME=%s"%targetPath.NAGIOS_HOME
    file=None
    delNagiosHomeToprofile()
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()  
 
        file.writelines(strforconfig+"\n") 
        
    except Exception,err:
        print  "addNagiosHomeToprofile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()  
#add config in nagios 
def reuseConfigfile():           
    cfgfile= targetPath().nagios_hw_ser_cfg()
    configBinPath=targetPath().nagios_bin()+"/huawei_server/config.py "
    if os.path.isfile(cfgfile):
        tmpcmd="python %s update"%configBinPath
        os.system(tmpcmd) 

def install():
    
    #clear env before install
    os.system("trapdNum=`ps -ef | grep trapd.py|grep python | grep -v grep | awk '{print $2}'` && if [ ! -e $trapdNum ]; then kill -9 $trapdNum; fi")
    os.system("collectNum=`ps -ef | grep collect.py|grep python | grep -v grep | awk '{print $2}'` && if [ ! -e $collectNum ]; then kill -9 $collectNum; fi")
    
    if ("__main__" == __name__) and checkpath() :
        if checkCfgTask.checkPathNot(targetPath().nagios_bin() + "/huawei_server/trapd.py") :
            LOG.error('Plug-in registrationed.Please uninstalled, try install.')
            raise InstallExcept()
        
        trapdcheck()
        '''
        '自动创建nagios用户目录
        '''
        try:
            os.makedirs('/home/nagios', 0775)           
        except OSError , why:
            pass
       
 
        '''
        '初始化
        '''
        #做一些初始化工作
        #更新initial.cfg文件 begin

        insertInitialCfg()
        #更新initial.cfg文件 end
        
        '''
        '移动python脚本至指定位
        '''
        
        moveFile()
        os.system("chmod  -R 700 "+targetPath().nagios_var()+os.path.sep+"huawei_server")
        os.system("chmod  -R 700 "+targetPath().nagios_bin()+os.path.sep+"huawei_server")
        os.system("chmod  -R 700 "+targetPath().nagios_libexec()+os.path.sep+"huawei_server")
        os.system("chmod  -R 700 "+targetPath().nagios_etc()+os.path.sep+"huawei_server")
        
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"configInfo.cfg")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"huawei_hosts.xml")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"initial.cfg")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"huawei_plugin.cfg")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"pluginConfig.xml")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"device.xml")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"device" + os.path.sep + "High-density_Common.xml")
        os.system("chmod  600 "+targetPath().nagios_etc()+os.path.sep+"huawei_server"+os.path.sep+"device" + os.path.sep + "Rack_Common.xml")
        
        os.system("chmod  600 "+targetPath().nagios_bin()+os.path.sep+"huawei_server"+os.path.sep+"constInfo.py")
        os.system("chmod  600 "+targetPath().nagios_bin()+os.path.sep+"huawei_server"+os.path.sep+"dataInfo.py")
        if CKmkVersion.getckmkVersion() == '1_4'or CKmkVersion.getckmkVersion() == '1_5':
            _currenPath =os.getcwd()  
            copyusrfilecmd="cp  '%s'/usrFile.cfg '%s'"%(_currenPath,targetPath().nagios_etc()+os.path.sep+"huawei_server")
            os.system (copyusrfilecmd)
            os.system("chown -R %s:%s %s"%( G_CMK_USER,G_CMK_GROUP, targetPath.NAGIOS_HOME) )
            
        else:
            os.system("chown -R %s:%s "%(G_NAGIOS_USER,G_NAGIOS_GROUP)+targetPath().nagios_bin()+os.path.sep+"huawei_server")
            os.system("chown -R %s:%s "%(G_NAGIOS_USER,G_NAGIOS_GROUP)+targetPath().nagios_etc()+os.path.sep+"huawei_server")
            os.system("chown -R %s:%s "%(G_NAGIOS_USER,G_NAGIOS_GROUP)+targetPath().nagios_libexec()+os.path.sep+"huawei_server")
            os.system("chown -R %s:%s "%(G_NAGIOS_USER,G_NAGIOS_GROUP)+targetPath().nagios_var()+os.path.sep+"huawei_server")
        #set ENV 
        addNagiosHomeToprofile()
        addckmkVersionToprofile()
        reuseConfigfile()


def uninstall(isRetain):
    # 
    if isRetain.upper() == 'YES':
        isSaveData = True
    else :
        isSaveData = False   

    delNagiosHomeToprofile()
    delckmkVersionToprofile()
    
    if checkpath() :
        
       
        os.system("trapdNum=`ps -ef | grep trapd.py |grep python| grep -v grep | awk '{print $2}'` && if [ ! -e $trapdNum ]; then kill -9 $trapdNum; fi")
        os.system("collectNum=`ps -ef | grep collect.py|grep python | grep -v grep | awk '{print $2}'` && if [ ! -e $collectNum ]; then kill -9 $collectNum; fi")
            
        removeFile(isSaveData)
        reEditFile()
        delInfoInNagiosCfg()
        delInfoInNagiosSourceFile()
        
        '''
        '重启nagios服务
        '''    
        if '1_4' in CKmkVersion.getckmkVersion() or  '1_5' in CKmkVersion.getckmkVersion(): 
            os.system("omd restart")
        else:     
            os.system("service nagios restart")
                    
        
def main():
    global G_NAGIOS_USER
    global G_NAGIOS_GROUP
    global G_CMK_USER
    global G_CMK_GROUP
    InitUserCfg().initCfg()

    MSG_USAGE = '''\n    %prog install -d LOCAL_ADDRESS [-p LISTEN_PORT] -n NAGIOS_DIR \
                   \nor\
                   \n    %prog uninstall  -n NAGIOS_DIR 
                '''
    optParser = OptionParser(MSG_USAGE)
    optParser.add_option("-d", "--local_address", action="store"
                         , dest="local_address"
                         , help="Local IP address (mandatory).  "
                         + "example:192.168.1.1")
    
    optParser.add_option("-p", "--listen_port", action="store"
                         , dest="listen_port" , default='10061'
                         , help="Listening port number. Default value: 10061")
    
    optParser.add_option("-n", "--nagios_dir", action="store"
                         , dest="nagios_dir"
                         , help="Nagios home directory (mandatory).         "
                         + "Example:/usr/local/nagios")
    optParser.add_option("-m", "--checkMKVersion", action="store"
                         , dest="checkMKVersion"
                         , help="assign checkMK version "
                         + "Example:1_4 for checkMK1.4 ")
    optParser.add_option("-s", "--retain", action="store"
                         , dest="retain"
                         , help="retain user date  yes for save date "
                         + "Example: 'yes', 'no' ")                     
    
    options, args = optParser.parse_args()

    #verify -m  
    if not options.checkMKVersion is None:
        if  not options.checkMKVersion  in CHECK_MK_VERSION_LIST:
            print "-m only suport as follow:"
            for vesionitem in CHECK_MK_VERSION_LIST:
                print vesionitem

    if len(args) == 1 and (args[0] == 'install' or  args[0] == 'uninstall'):
        if args[0] == 'uninstall':
            if options.nagios_dir is None:
                print "please input nagios dir "
                exit()
            if not options.checkMKVersion is None:
                CKmkVersion.setckmkVersion(options.checkMKVersion)
            else: 
                CKmkVersion.setckmkVersion(CKmkVersion.find_ckmkVersion())
            try :  
                if '1_4' in CKmkVersion.getckmkVersion() or  '1_5' in CKmkVersion.getckmkVersion(): 
                    targetPath.NAGIOS_HOME= re.sub(r'[/|\\]*$', '', options.nagios_dir)+"/"+"nagiosPlugInForHuawei"  
                    G_CMK_USER,G_CMK_GROUP = getUsrInfo()
                else :  
                    G_NAGIOS_USER,G_NAGIOS_GROUP = getNagiosUserinfo()  
                    targetPath.NAGIOS_HOME= re.sub(r'[/|\\]*$', '', options.nagios_dir)
                if  options.retain is not None:   
                    uninstall(options.retain)
                else :
                    uninstall('no')  
            except HelpExcept:
                optParser.print_help()
            except InstallExcept, exc:
                LOG.error(str(exc.message) + 'uninstall fail.')
                print 'Done.'
            else:
                LOG.info('uninstall success.');
                print 'Done.'
        elif  args[0] == 'install':
            if options.local_address is not None and options.nagios_dir is not None:
                try:
                    checkip(options.local_address)
                    targetPath.NAGIOS_LOCAL_ADDRESS = options.local_address
                    targetPath.NAGIOS_HOME = re.sub(r'[/|\\]*$', '', options.nagios_dir)
                    
                    if None != options.listen_port :
                        targetPath.NAGIOS_LISTEN_PORT = options.listen_port
                    if not options.checkMKVersion is None:
                        CKmkVersion.setckmkVersion(options.checkMKVersion)
                        if '1_4' in options.checkMKVersion or  '1_5' in options.checkMKVersion:
                            G_CMK_USER,G_CMK_GROUP = getUsrInfo()
                            targetPath.NAGIOS_HOME = re.sub(r'[/|\\]*$', '', options.nagios_dir)+"/"+"nagiosPlugInForHuawei"   
                        else:
                           
                            G_NAGIOS_USER,G_NAGIOS_GROUP = getNagiosUserinfo()     
                    install()

                except HelpExcept:
                    optParser.print_help()
                except InstallExcept, exc:
                    LOG.error(str(exc.message) + 'install fail.')
                    print 'Done.'
                else:
                    LOG.info('install success.')
                    print 'Done.'     
        else:
            optParser.print_help()
    else:
        optParser.print_help()
    

main()
