#!/bin/bash

if [ $# == 2 ];then
    if [ $1 == "-H" ];then
        hostip=$2
        cmd="python /usr/local/nagios/bin/huawei_server/collect.py -p 2>&1 | grep ${hostip}| grep \;system\;"
    else
        echo "please input host ip!"
        exit 3
    fi
elif [ $# == 4 ];then
    if [ $1 == "-H" ] && [[ $3 == "-S" ]];then
        hostip=$2
        device=$4
    elif [[ $1 == "-S" ]] && [[ $2 == "-H" ]];then
        hostip=$4
        device=$2
    else
        echo "please input command as:getInfo.sh -H 192.168.3.1 -S cpu/memory/hardDisk/fan/power/system"
        exit 3
    fi

    if [ $device != "cpu" ] && [ $device != "memory" ] && [ $device != "hardDisk" ] && [ $device != "fan" ] && [ $device != "power" ] && [ $device != "system" ];then

        echo "please input command as:getInfo.sh -H 192.168.3.1 -S cpu/memory/hardDisk/fan/power/system"
        exit 3
    fi

    cmd="python /usr/local/nagios/bin/huawei_server/collect.py -p 2>&1 | grep ${hostip} | grep \;${device}\;"
else
   echo "please input command as:getInfo.sh -H 192.168.3.1 -S cpu/memory/hardDisk/fan/power/system"
   exit 3
fi

result=$(eval $cmd)
status=${result#*;}
echo $status

ret=$(echo $status |awk -F ';' '{print $3}')
exit $ret

