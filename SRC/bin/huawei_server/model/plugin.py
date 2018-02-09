#encoding:utf-8

class LoggerConfig:
    
    def __init__(self):
        self._loggerPath = "";         #日志路径
        self._loggerLevel = "";        #日志级别
        self._loggerSize = "";     #日志文件大小
        self._loggerIndex ="";     #日志文件个数
        
    def getLoggerPath(self):
        return self._loggerPath;
        
    def setLoggerPath(self, loggerPath):
        self._loggerPath = loggerPath;

    def getLoggerLevel(self):
        return self._loggerLevel;
        
    def setLoggerLevel(self, loggerLevel):
        self._loggerLevel = loggerLevel;
        
    def getLoggerSize(self):
        return self._loggerSize;
        
    def setLoggerSize(self, loggerSize):
        self._loggerSize = loggerSize;
        
    def getLoggerIndex(self):
        return self._loggerIndex;
        
    def setLoggerIndex(self, loggerIndex):
        self._loggerIndex = loggerIndex;
        
    