#encoding:utf-8

import sys
import types

from xml.etree import ElementTree
from xml.dom import minidom

sys.path.append("..")
from model.result import CollectResult, ChannelResult
from base.logger import Logger
from util.common import Common
from constant.constant import *



class ProcessService:
    _logger = Logger.getInstance();
    
    @classmethod
    def start(cls, mode, targetPath, collectResult):
           
        if NUMBER_ZERO == len(collectResult.getService()):
            cls._logger.error("process start: %s host has no collection module service" % collectResult.getHostName());
            return;   
        
        if COLLECT_MODE_CMD_PLUGIN == mode:
            cls.basicProcess(collectResult);
        else:
            cls.extensionProcess(targetPath, collectResult);
    
    #采集结果转成nagios命令
    @classmethod
    def basicProcess(cls, collectResult):
            
        for service in collectResult.getService():
            
            status = "";
            information = "";
            componentResult = collectResult.getService()[service];
            if componentResult is None or type(componentResult) is types.IntType:
                status = NAGIOS_STATUS_UNKNOWN;
                information = NAGIOS_INFORMATION_UNKNOWN;
            
            else:
                for item in componentResult:
                    component = item.getComponent();
                    result = item.getResult();
                    
                    if "on" == component.getState():
                        status = cls.__statusProcess(component, result);
                    
                    else:
                        information += cls.__informationProcess(component, result) + NAGIOS_INFORMATION_SEP;
                    
            message = Common.constructMessage(collectResult.getHostName(), service, status, information);
            cls._logger.error("basic process: nagios cmd message is %s" % message);
            Common.writeCmd(message)    
    
    #E9000暂不支持
    @classmethod    
    def __statusProcess(cls, component, result):
        
        if result.getCode() != NAGIOS_ERROR_SUCCESS:
            return NAGIOS_STATUS_UNKNOWN;
        
        if "get" == component.getMethod():
            
            node = component.getNode()[0];
            if not result.getData().has_key(node.getOid()):
                return NAGIOS_STATUS_UNKNOWN;
            return node.getReplace()[result.getData()[node.getOid()]];
        
        if "bulk" == component.getMethod():
            cls._logger.error("status process: method is not get" % component.getMethod());
            return NAGIOS_STATUS_UNKNOWN;
            
    @classmethod        
    def __informationProcess(cls, component, result):
        
        if result.getCode() != NAGIOS_ERROR_SUCCESS:
            return str({node.getName(): result.getDetail() for node in component.getNode()});
                
        if "get" == component.getMethod():
            message = {}
            for node in component.getNode():
                message[node.getName()] = node.getReplace()[result.getData()[node.getOid()]] if (len(node.getReplace()) != 0) else result.getData()[node.getOid()]; 
            
            return str(message).replace("{", "").replace("}", "").replace(" ", "").replace(",", "/  ");
            
        elif "bulk" == component.getMethod():
            message = {};
            nodeName = [];
            validInstance = [];
            for node in component.getNode():
                value = {item[0].replace(node.getOid(), node.getName()): item[1] if not node.getReplace().has_key(item[1]) else node.getReplace()[item[1]]
                          for item in result.getData().items() if item[0].startswith(node.getOid() + ".")};
                if NUMBER_ZERO == len(value):
                    cls._logger.error("process information: the result of %s has not include in %s" % (node.getOid(), result.getData()));
                    continue;
                
                nodeName.append(node.getName());
                if "presence" == component.getShow():
                    message[node.getName()] = str(len({item[0]:item[1] for item in value.items() 
                                                       if (item[1] == "presence") or (item[1] != "absence")})) + "/" + str(len(value));
                if node.getValue() == "empty":
                    for item in value.items():
                        if item[1] == '' or item[1] == '0':
                             continue;
                        message[item[0]] = item[1];
                        instance = cls.__instanceToInt(item[0].replace(node.getName(), ''));
                        if "" == instance:
                            continue;
                        validInstance.append(instance);
                else:
                    message.update({item[0]:item[1] for item in value.items() if cls.__instanceToInt(item[0].replace(node.getName(), '')) in validInstance});                                       
                
               
            if "empty" == component.getShow():
                message = [str(name + "." + str(instance) + ":" + message[name + "." + str(instance)]) for instance in sorted(validInstance) for name in nodeName];
                 
            return (str(message).replace("{", "").replace("}", "").replace(",", "/  ") if type(message) is types.DictType else str(message).replace("[", "").replace("]", "")).replace("'", '').replace(",", "/  ");
            
        else:
            cls._logger.error("process information: it has not this %s method." % component.getMethod());
            return NAGIOS_INFORMATION_UNKNOWN;


    @classmethod
    def __instanceToInt(cls, instance):
        if instance == "":
            return instance;
        
        try:
           value = int(instance.replace(".", ""));
            
        except ValueError:
            cls._logger.error("covert instance: %s is not pure numeric string." % instance.replace(".", ""));
            return "";
        
        return value;
        
    #采集结果转成xml文件
    @classmethod
    def extensionProcess(cls, targetPath, collectResult):
        
        #XML根节点
        root = ElementTree.Element(collectResult.getHostName()); 
        root.set("ip", collectResult.getIpAddress());
        
        for service in collectResult.getService():
            
            module = ElementTree.SubElement(root, service)
            
            componentResult = collectResult.getService()[service];
            if componentResult is None or type(componentResult) is types.IntType:
                module.text = NAGIOS_INFORMATION_UNKNOWN;
            else:
                for item in componentResult:
                    cls.__detailProcess(module, item.getComponent(), item.getResult());
        
        Common.indent(root)
        tree = ElementTree.ElementTree(root)
        tree.write(Common.getFilePath(targetPath, collectResult.getHostName(), collectResult.getIpAddress()), "utf-8")

                            
    @classmethod                    
    def __detailProcess(cls, module, component, result):
        
        if "get" == component.getMethod():
            for node in component.getNode():
                element = ElementTree.SubElement(module, node.getName())
                element.text = node.getReplace()[result.getData()[node.getOid()]] if (len(node.getReplace()) != 0) else result.getData()[node.getOid()]; 

        elif "bulk" == component.getMethod():
            instances = [];
            names = [];
            message = {};
            for node in component.getNode():
                value = {item[0].replace(node.getOid(), node.getName()): item[1] if not node.getReplace().has_key(item[1]) else node.getReplace()[item[1]]
                          for item in result.getData().items() if item[0].startswith(node.getOid() + ".")};
                
                if NUMBER_ZERO == len(value):
                    cls._logger.error("process information: the result of %s has not include in %s" % (node.getOid(), result.getData()));
                    continue;
                
                if NUMBER_ZERO == len(instances):
                    instances = [item[0].replace(node.getName(), '') for item in value.items()];
                
                names.append(node.getName());                                  
                message.update(value);
            
            if NUMBER_ONE == len(instances):
                elements = ElementTree.SubElement(module, "component");
                for key in message:
                    element = ElementTree.SubElement(elements, key);
                    element.text = message.get(key);                    
            else:
                for instance in instances:
                    elements = ElementTree.SubElement(module, "component");
                    for name in names:
                        element = ElementTree.SubElement(elements, name + instance);
                        element.text = message[name + instance];
                
        else:
            cls._logger.error("process information: it has not this %s method." % component.getMethod());
            module.text = NAGIOS_INFORMATION_UNKNOWN;
    

    

    
    
    
    
    
          