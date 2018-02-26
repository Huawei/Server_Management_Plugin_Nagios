#encoding:utf-8

import os
import sys


from processservice import ProcessService
from parsehostxml import ParseHostXml
from parsedevicexml import ParseDeviceXml

sys.path.append("..")
from base.logger import Logger
from base.channel import Channel
from util.common import Common 
from model.device import Device
from model.result import CollectResult, ComponentResult
from constant.constant import *


class CollectService:
    _logger = Logger.getInstance();
    _configs = [];
    
    def __init__(self, mode, data):
        self._mode = mode;
        self._targetPath = Common.getBinPath() + os.path.sep + "result";
        self._hostPath = Common.getHostConfigPath(); 
        if COLLECT_MODE_CMD_TOTAL == mode and NUMBER_TWO == len(data):
            self._targetPath = data[1];
        elif COLLECT_MODE_CMD_FILE == mode and NUMBER_ONE == len(data):
            self._hostPath = data[0] if data[0][len(data[0])-1:] != os.path.sep else data[0][0:len(data[0])-1];
        elif COLLECT_MODE_CMD_FILE == mode and NUMBER_THREE == len(data):
            self._hostPath = data[0];
            self._targetPath = data[2] if data[2][len(data[2])-1:] != os.path.sep else data[2][0:len(data[2])-1];
            
        if not ParseDeviceXml.parseDeviceXml(Common.getDeviceConfigPath(), self._configs):
            self._logger.error("service : parse device xml file failed");
        
    def start(self):
        hosts = [];
        if not ParseHostXml.parseHostXml(self._hostPath, hosts):
            self._logger.error("service : parse host xml file failed.");
            return -1;
        
        for host in hosts:
            
            channel = Channel(host);
           
            collectResult = CollectResult();
            collectResult.setHostName(host.getHostName()); 
            collectResult.setIpAddress(host.getIpAddress());
            
            deviceInfo = Device();
            
            errCode = self.__getDeviceInfo(channel, host, deviceInfo);
            if errCode != NAGIOS_ERROR_SUCCESS:
                self._logger.error("service : get device info failed. host name:%s" % host.getHostName());
                collectResult.setService({service: errCode for service in (host.getCollectBasic() if (COLLECT_MODE_CMD_PLUGIN == self._mode) else host.getCollectExtension())})
            
            else:
                collectResult.setService(self.collect(channel, host, deviceInfo));
            
            ProcessService.start(self._mode, self._targetPath, collectResult);
            
        return 0;
        
    
    def collect(self, channel, host, deviceInfo):
        
        collectComponents = host.getCollectBasic() if (COLLECT_MODE_CMD_PLUGIN == self._mode) else host.getCollectExtension();
        
        serviceResult = {}
        for collectComponent in collectComponents:
            
            if not deviceInfo.getComponents().has_key(collectComponent):
                self._logger.error("service: collect device info failed. device config not has %s component in %s host." % (collectComponent, host.getHostName()));
                serviceResult[collectComponent] = NAGIOS_ERROR_DEVICE_CONFIG_NOTINCLUDE;
            
            else:
                componentResults = [];
                for deviceComponent in deviceInfo.getComponents()[collectComponent]:
                    componentResult = ComponentResult();
                    componentResult.setComponent(deviceComponent);
                    componentResult.setResult(self.__collectNode(channel, deviceComponent));
                    componentResults.append(componentResult);
                    
                serviceResult[collectComponent] = componentResults;
        
        return serviceResult; 
                
                
    #采集node节点中的OID信息
    def __collectNode(self, channel, deviceComponent):
        
        nodeOids = [deviceNode.getOid() for deviceNode in deviceComponent.getNode()]
        
        if "get" == deviceComponent.getMethod():
        
            return  channel.getCmd(*tuple(nodeOids))
        
        elif "bulk" == deviceComponent.getMethod():
            return  channel.bulkCmd(0, 1, *tuple(nodeOids))
        else:
            self._logger.error("service: collect device info failed， the %s  method of request is invalid." % (deviceComponent.getMethod()));
            return ChannelResult(NAIGOS_ERROR_INVALID_METHOD);        
    
    #获取host设备采集信息
    def __getDeviceInfo(self, channel, host, device):
        
        config = self.__getDeviceConfig(host.getDeviceType())
        if config is None:
           self._logger.error("service: get device config failed. device type:%s." % (host.getDeviceType()));
           return NAGIOS_ERROR_DEVICE_XML_INVALID;
        
        deviceModel = self.__getDeiveModel(channel, config.getOid());
        if deviceModel is None:
           self._logger.error("service: get device model failed. host name:%s, device type oid:%s." % (host.getHostName(), config.getOid()));
           return NAGIOS_ERROR_DEVICE_XML_INVALID;
        

        deviceConfigPath = self.__getConfigPath(config, deviceModel);
        errCode = ParseDeviceXml.parseDeviceConfig(self._mode, deviceConfigPath, device)
        if errCode != NAGIOS_ERROR_SUCCESS:
            self._logger.error("service: parse device config failed. host name:%s, device model:%s." % (host.getHostName(), deviceModel));
            return errCode;
        
        return NAGIOS_ERROR_SUCCESS;
    
    def __getConfigPath(self, config, deviceModel):
        
        for file in config.getFile():
            if deviceModel == file.getType() or deviceModel in file.getReplace():
                return Common.getDeviceModelPath() + os.path.sep + file.getName();
            
        return self.__getCommonConfigPath(config);
        
    
    def __getCommonConfigPath(self, config):
        for file in config.getFile():
            if "common" == file.getType():
                return Common.getDeviceModelPath() + os.path.sep + file.getName();
        
        return None;
    
            
    #获取host设备的型号
    def __getDeiveModel(self, channel, oid):
       
       reslut = channel.getCmd(oid);
       if reslut.getCode() != NAGIOS_ERROR_SUCCESS:
           return None;

       return reslut.getData()[oid];
           
           
    #获取host设备的型号OID
    def __getDeviceConfig(self, deviceType):
       
       for config in self._configs:
           if deviceType == config.getDeviceType():
               return config;
       return None; 

        
        
        
        
        
        
        
        
