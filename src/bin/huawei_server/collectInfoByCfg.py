#coding=utf-8
import os
import sys
import commands
import time
import re

def find_nagiosdir():
    '''return nagios directory'''
    cmd = "source /etc/profile;echo $NAGIOSHOME"
    procs = commands.getoutput(cmd)
    return procs
def getCfgfile():
    nagios_home= find_nagiosdir() 
    return nagios_home + "/etc/huawei_server/hw_server.cfg"

def getUser5info():
    nagios_home= find_nagiosdir() 
    return nagios_home + "/libexec"
USER5INFO= getUser5info()
def main():
    file = None
    try :
        file = open(getCfgfile(),"r+")
        strlist=file.readlines()
        file.close()
        for strlines  in strlist :
            if 'command_line' in strlines and '-T Blade' in strlines:
                comd = strlines.replace ( "command_line","" ).replace("$USER5$",USER5INFO)
                os.system(comd )                      
    except Exception,err:
        print "writeCmd error: " +str(err)
    finally:
        if file is not None:
            file.close()
main()