#encoding:utf-8

import os
import sys
import logging
import logging.handlers
import threading

sys.path.append("..")
from model.plugin import LoggerConfig 

LEVEL = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }


#日志管理类
class Logger:
    
    _mutex = threading.Lock()
    _instance = None;
    _logger = logging.getLogger("huawei_plugin");
    
    def __init__(self):
        pass;
       
    #单例模式
    @staticmethod
    def getInstance():
        if None == Logger._instance:
            Logger._mutex.acquire();
            if None == Logger._instance:
                Logger._instance = Logger();
            Logger._mutex.release()

        return Logger._instance;

    def init(self, loggerConfig):
        
        self._logger.setLevel(LEVEL.get(loggerConfig.getLoggerLevel()));
        
        format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s");
        
        #配置命令行日志־
        streamHandler = logging.StreamHandler();
        streamHandler.setFormatter(format);
        streamHandler.setLevel(LEVEL.get(loggerConfig.getLoggerLevel()));
        
        
        #配置文件日志
        if not os.path.exists(loggerConfig.getLoggerPath()):
            os.makedirs(loggerConfig.getLoggerPath());
        
        logPath = loggerConfig.getLoggerPath() +  os.path.sep + "plugin.collect.log";
            
        fileHandler = logging.handlers.RotatingFileHandler(logPath, loggerConfig.getLoggerSize(), loggerConfig.getLoggerIndex());
        fileHandler.setFormatter(format);
        fileHandler.setLevel(LEVEL.get(loggerConfig.getLoggerLevel()));
        
        self._logger.addHandler(streamHandler);
        self._logger.addHandler(fileHandler);
        
      
    def info(self, message):
        self._logger.info(message);
        
    def debug(self, message):
        self._logger.debug(message);
        
    def warning(self, message):
        self._logger.warning(message);
        
    def error(self, message):
        self._logger.error(message);
        
    def exception(self, message):
        self._logger.exception(message);
    
    def critical(self, message):
        self._logger.critical(message);
        
        
 