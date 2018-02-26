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


this_file = inspect.getfile(inspect.currentframe())
file_dir, file_name = os.path.split(this_file)
if file_dir == '' :
    file_dir = os.getcwd()

'''
==================================
日志
==================================
'''
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
 
'''
'移动python脚本至指定位
'''   
def moveFile():
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
def editFile():
    LOG.info('editFile begin.')
#   修改cgi.cfg
    cfgEid2 = True
    
    cgiCfgPt = 'escape_html_tags='
    cgiCfg = 'escape_html_tags=0'
    ptCgiCfg = r'^\s*escape_html_tags=\s*\d\s*$'
    cfgEid3 = fileMrg.readEditFile(targetPath().nagios_cgi_config(), cgiCfg, cgiCfgPt, ptCgiCfg)
    LOG.info('editFile end.')
    return True and cfgEid1 and cfgEid2 and cfgEid3

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
     trapdNum=`ps -efww | grep trapd.py | grep -v grep | awk '{print $2}'`
}

collectNum=NULL
function getCollectNum()
{
     collectNum=`ps -efww | grep collect.py | grep -v grep | awk '{print $2}'`
}

function kill()
{
    killNum=`kill -9 $1`; 
}


function startTrapd()
{
    su - nagios
    cd `dirname $0`
    nohup python '''+targetPath().nagios_bin()+os.path.sep+'''huawei_server'''+os.path.sep+'''trapd.py > /dev/null 2>&1 &
}


function startCollect()
{
    su - nagios
    cd `dirname $0`
    nohup python '''+targetPath().nagios_bin()+os.path.sep+'''huawei_server'''+os.path.sep+'''collect.py -p > /dev/null 2>&1 &
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
    
    echo "OK"
    exit 0
}
source /etc/profile
export PATH="%s:$PATH"
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
    
def addNagiosHomeToprofile():
    FilePath="/etc/profile"
    strforconfig="export NAGIOSHOME=%s"%targetPath.NAGIOS_HOME
    file=None
    try:
        file = open(FilePath,"r+")
        strlist=file.readlines()  
        #had configed so exit             
        for i in range(len(strlist)):
            if strforconfig in str(strlist[i]):
                 return
        #cofnig   nagios.cfg  
        file.writelines(strforconfig+"\n") 
        
    except Exception,err:
        print  "addNagiosHomeToprofile exception info :" + str(err)  
    finally:
        if file is not None:
            file.close()  
            
def delNagiosHomeToprofile(): 
    FilePath="/etc/profile"
    strforconfig="export NAGIOSHOME=%s"%targetPath.NAGIOS_HOME
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
def install():
    
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
        
        os.system("chown -R nagios:nagios "+targetPath().nagios_bin()+os.path.sep+"huawei_server")
        os.system("chown -R nagios:nagios "+targetPath().nagios_etc()+os.path.sep+"huawei_server")
        os.system("chown -R nagios:nagios "+targetPath().nagios_libexec()+os.path.sep+"huawei_server")
        os.system("chown -R nagios:nagios "+targetPath().nagios_var()+os.path.sep+"huawei_server")
        #set ENV 
        addNagiosHomeToprofile()


def uninstall():
    #获得安装时的路径
    initial_cfg = open(targetPath.CURR_PATH + '/etc/huawei_server/initial.cfg')
    '''
    'nagios_dir
    'nagios_cmd_file
    'cache_path
    '''
    for pro in initial_cfg:
        if re.findall(r'^\s*nagios_dir\s*=\s*/', pro):
            targetPath.NAGIOS_HOME = re.sub(r'\s*$','',pro.split('=')[1])
        elif re.findall(r'^\s*nagios_cmd_file\s*=\s*/', pro):
            targetPath.NAGIOS_CMD = re.sub(r'\s*$','',pro.split('=')[1])
        elif re.findall(r'^\s*cache_path\s*=\s*/', pro):
            targetPath.NAGIOS_CACHE_PATH = re.sub(r'\s*$','',pro.split('=')[1])
    #set ENV 
    delNagiosHomeToprofile()
    
    if checkpath() :
        isSaveData = True
        while True:
            #希望保留用户数据
            isY = raw_input("Do you want to retain user data?(Y/N)")
            if isY == 'Y' or isY == 'N' or isY == 'y' or isY == 'n' :
                break;
            #你输入的选项不正确,请重新选择
            LOG.info("The option you selected is incorrect. Please reselect.");
        
        os.system("trapdNum=`ps -ef | grep trapd.py | grep -v grep | awk '{print $2}'` && if [ ! -e $trapdNum ]; then kill -9 $trapdNum; fi")
        os.system("collectNum=`ps -ef | grep collect.py | grep -v grep | awk '{print $2}'` && if [ ! -e $collectNum ]; then kill -9 $collectNum; fi")
                
        if isY == 'N' or isY == 'n':
            isSaveData = False
        removeFile(isSaveData)
        reEditFile()
        
        '''
        '重启nagios服务
        '''    
        os.system("service nagios restart")
             
        
def main():
    InitUserCfg().initCfg()

    MSG_USAGE = '''\n    %prog install -d LOCAL_ADDRESS [-p LISTEN_PORT] -n NAGIOS_DIR \
                   \nor\
                   \n    %prog uninstall
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
    
    
    options, args = optParser.parse_args()
    if len(args) == 1 and (args[0] == 'install' or  args[0] == 'uninstall'):
        if args[0] == 'uninstall':
            try:
                uninstall();
            except HelpExcept:
                optParser.print_help()
            except InstallExcept, exc:
                LOG.error(str(exc.message) + 'uninstall fail.')
                print 'Done.'
            else:
                LOG.info('uninstall success.');
                print 'Done.'
        elif options.local_address is not None and options.nagios_dir is not None:
            try:
                checkip(options.local_address)
                targetPath.NAGIOS_LOCAL_ADDRESS = options.local_address
                targetPath.NAGIOS_HOME = re.sub(r'[/|\\]*$', '', options.nagios_dir)

                if None != options.listen_port :
                    targetPath.NAGIOS_LISTEN_PORT = options.listen_port

                print install
                install()
                pass
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
    else :
        optParser.print_help()
    

main()
