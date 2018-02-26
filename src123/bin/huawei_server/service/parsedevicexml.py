#encoding:utf-8

import os
import sys
from xml.dom.minidom import Element

sys.path.append("..")
from util.common import Common 
from base.logger import Logger
from constant.constant import *
from model.device import *

class ParseDeviceXml:
    
    _logger = Logger.getInstance();
    
    @classmethod
    def parseDeviceXml(cls, configPath, configs):
        
        if not os.path.exists(configPath):
            cls._logger.error("parse device xml: file is not exist");
            return False;
        
        root = Common.getRoot(configPath);
        if root is None:
            cls._logger.error("parser device xml: device xml format is not valid.");
            return False;      
        
        for node in Common.getChild(root):
            
            if "Rack" != node.tag and "HighDensity" != node.tag and "E9000" != node.tag:
                cls._logger.error("parser device xml: config node should not has %s node." % node.tag);
                return False;
            
            config = Config();
            files = [];
            config.setDeviceType(node.tag);
            config.setOid(node.attrib.get("oid"));
            if not cls.__parseFileNode(node, files):
                cls._logger.error("parser device xml: file node format is not valid.");
                return False;
            config.setFile(files);
            
            configs.append(config);
            
        return True;
    
    @classmethod
    def __parseFileNode(cls, node, files):
        
        elements = Common.getChild(node);
        if elements is None:
             cls._logger.error("parser file node: %s node has no child node." % node.tag);
             return False;
                
        for element in elements:
                
            if "file" != element.tag:
                cls._logger.error("parser file node: element tag is not file.");
                return False;
                 
            file = File();
            file.setType(element.attrib.get("type"));
            file.setName(element.text);
            files.append(file);
                
        return True;
            
    @classmethod    
    def parseDeviceConfig(cls, mode, configPath, device):
        
        if not os.path.exists(configPath):
            cls._logger.error("parse device config: file is not exist");
            return NAGIOS_ERROR_DEVICE_CONFIG_NOTEXIST;
        
        root = Common.getRoot(configPath);
        if root is None:
            cls._logger.error("parser device config: device config format is not valid.");
            return NAGIOS_ERROR_DEVICE_FORMAT_INVALID;
                
        device.setDeviceModel(root.attrib.get("devType"));
        components = {};
        for node in Common.getChild(root):
            
            component = [];
            if not cls.__parseComponentNode(mode, node, component):
                cls._logger.error("parser device config: child node format is not valid.");
                return NAGIOS_ERROR_DEVICE_FORMAT_INVALID;
            
            components[node.tag] = component;
            
        device.setComponents(components);
        
        return NAGIOS_ERROR_SUCCESS;
            
    @classmethod
    def __parseComponentNode(cls,  mode, node, component):
        
        elements = Common.getChild(node);
        if elements is None:
            cls._logger.error("parser component node: %s node has no child node." % node.tag);
            return False;
        
        for element in elements:
            
            if "basic" != element.tag and "extension" != element.tag:
                cls._logger.error("parser component node: %s node should not has %s node." % (node.tag, element.tag));
                return False;
            
            if  COLLECT_MODE_CMD_PLUGIN == mode:
                
                if  "basic" != element.tag:
                    continue;
                
                if not cls.__parseModuleNode(element, component):
                    cls._logger.error("parser component node: basic node format is not valid.");
                    return False;
            else :
                
                if  "extension" != element.tag:
                    continue;
                
                if not cls.__parseModuleNode(element, component):
                    cls._logger.error("parser component node: extension node format is not valid.");
                    return False;
            
        return True;
    
    @classmethod
    def __parseModuleNode(cls, node, components):
        
        elements = Common.getChild(node);
        if elements is None:
            cls._logger.error("parser module node: %s node has no child node." % node.tag);
            return False;
        
        for element in elements:
            
            if "node" != element.tag:
                cls._logger.error("parser module node: element tag is not node.");
                return False;
            
            component = Component();
            component.setMethod(element.attrib.get("method"));
            component.setState(element.attrib.get("state"));
            component.setShow(element.attrib.get("show"));
            
            nodes = [];
            if not cls.__parseOidNode(element, nodes):
                cls._logger.error("parser module node: oid node format is not valid.");
                return False
            
            component.setNode(nodes);
            
            components.append(component);
            
        return True;     
        
    @classmethod    
    def __parseOidNode(cls, node, nodes):
        
        elements = Common.getChild(node);
        if elements is None:
            cls._logger.error("parser oid node: %s node has no child node." % node.tag);
            return False;
        
        for element in elements:
            
            if "oid" != element.tag:
                cls._logger.error("parser oid node: element tag is not oid.");
                return False;
            
            node = Node();
            node.setName(element.attrib.get("name"));
            node.setOid(element.text);
            node.setValue(element.attrib.get("value"));

            if element.attrib.get("range") is not None:
                node.setRange(element.attrib.get("range"));
            
            node.setReplace(cls.__convertStrToDict(element.attrib.get("replace")));
            
            nodes.append(node);
            
        return True;
    
    @classmethod     
    def __convertStrToDict(cls, replace):
        
        if replace is None:
            return {};
        
        values = replace.split(",");
        
        replaces = {};
        for value in values:
            if 2 != len(value.split(":")):
                cls._logger.error("str to dict: %s is not in the colon as a separator." % value);
                continue;
            replaces[value.split(":")[0]] = value.split(":")[1];
        
        return replaces; 
        
        
                         
            
            