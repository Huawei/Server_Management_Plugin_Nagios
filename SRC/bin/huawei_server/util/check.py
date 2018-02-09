#encoding:utf-8

import os
import sys
from Crypto.Util import number

sys.path.append("..")
from base.logger import Logger
from constant.constant import *

#参数校验类
class Check:
    
    _logger = Logger.getInstance();
    
    @classmethod
    def checkPluginModeParam(cls, params):
        if NUMBER_ZERO == len(params):
            return True;
        return False;
    
    @classmethod
    def checkTotalModeParam(cls, params):
        if NUMBER_ZERO == len(params):
            return True;
        
        if NUMBER_TWO == len(params):
            return cls.checkTargetParam(params)
        
        return False;
    
    @classmethod
    def checkFileModeParam(cls, params):
        if NUMBER_ONE == len(params):
            if os.path.isfile(params[0]) and os.path.splitext(params[0])[1] == ".xml":
                cls._logger.error("check file mode: the host config file is invalid when param len is two");
                return True;
            
        if NUMBER_THREE == len(params):
            if os.path.isfile(params[0]) and os.path.splitext(params[0])[1] == ".xml":
                return cls.checkTargetParam(params[1:]);
        
        return False;
         
    #结果文件存放参数校验
    @classmethod
    def checkTargetParam(cls, params):
        if "-r" != params[0]:
            cls._logger.error("check target param: the second command is not -r.");
            return False;
        if not os.path.isdir(params[1]):
            cls._logger.error("check target param: the target path is invalid.");
            return False;
        return True;
        
                