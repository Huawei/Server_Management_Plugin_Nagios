#coding=utf-8

import ConfigParser
import getpass
import os
import sys
import constInfo
import dataInfo
import commands
'''
' 文件操作类异常
' handle: 处理文件操作异常信息类, 
'''
class FileExcept(Exception):
    pass

'''
' 读取文件信息
' methods: readKey 读取目标文件信息
' return: 返回文件信息    
'''
def find_nagiosdir():
    '''return nagios directory'''
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)
    return procs 
def readKey():
    try:
        # k文件路径
        kfilepath = find_nagiosdir() + os.path.sep +'etc' + os.path.sep \
                       + 'huawei_server' + os.path.sep \
                       + 'configInfo.cfg'
        file = open(kfilepath, constInfo.FILE_R)
        key = file.readline()

    except IOError, err:
        raise FileExcept(dataInfo.WRITE_FILE_ERROR \
                              + str(err))
        file.close()
    except Exception, err:
        raise FileExcept(\
                    dataInfo.WRITE_FILE_UNKNOWN \
                    + str(err))
        file.close()
    else:
        file.close()
    if key is not None :
        return key
    else:
        return constInfo.DATA_CONS

'''
' 加密信息
' methods: encryptKey 待加密字符串
' return: 返回加密字符串    
'''
def encryptKey(pkey, rootkey):
    
    if rootkey is not None:
        encryptStr = os.popen("echo " + "'" + pkey + "'" +  " | openssl aes-256-cbc -k " + "'" +  rootkey +  "'" + " -base64")\
                                        .read().strip()
    return encryptStr    

'''
' 解密信息
' methods: encryptKey 解密加密字符串
' return: 返回解密字符串    
'''
def dencryptKey(pkey, rootkey):
    
    if rootkey is not None:
        encryptStr = os.popen("echo " +  "'" + pkey +  "'" + " | openssl aes-256-cbc -d -k " + "'" +  rootkey + "'" +  " -base64")\
                                        .read().strip()
    return encryptStr        


'''
' 读取文件信息
' methods: genRootKeyStr 读取目标文件信息
' return: 返回文件信息    
''' 


def genRootKeyStr():
    configfilepath = find_nagiosdir() + os.path.sep +'etc' + os.path.sep \
                       + 'huawei_server' + os.path.sep \
                       + 'initial.cfg'
    parser = ConfigParser.ConfigParser()
    configdata = {}
    rootkey = ""
    try:
        file = open(configfilepath, constInfo.FILE_R)
        parser.readfp(file)
        for section in parser.sections():
            for (key, value) in parser.items(section):
                configdata[key] = value
        rootkey = configdata.get(constInfo.NAGIOS_CONTANT3)

    except IOError, err:
        file.close()
        raise FileExcept(dataInfo.OPEN_FILE_ERROR + '\n' + str(err))
    except FileExcept, err:
        file.close()
        raise
    except Exception, err:
        file.close()
        raise FileExcept(dataInfo.INITIAL_FILE + '\n' + str(err))
    else:
        file.close()
        
    if rootkey is not None :
        key = dataInfo.CONSTANT1 + rootkey + constInfo.CONSTANT2
        return key
    else:
        raise FileExcept(dataInfo.ROOTKEY_UNKNOWN + '\n' + str(err))

'''
' 工具方法，加密用户密码信息
' methods: encryptPwd 加密用户需要的信息
' return: 加密密文    
''' 
def encryptPwd():

    if (len(sys.argv) == 2 and "encryptPwd" == sys.argv[1]):
        pkey = getpass.getpass(dataInfo.INPUT_PWD)
        
        try:
            if pkey is not None :
                key = readKey()
              
                rootKey = genRootKeyStr()
                k = dencryptKey(key, rootKey)
                print encryptKey(pkey, k)
                return
        except FileExcept:
            print dataInfo.PWD_UNKNOWN

encryptPwd()