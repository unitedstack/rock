#!/bin/bash

file='/usr/local/bin/ha_status'
ha_status=`cat $file`
if [ "$ha_status" != "master" ]; then
	exit 0
fi

echo 'aaa' >> ~/a.txt

rock_mon="rock-mon"
rock_engine="rock-engine"


var=`ps -ef | grep -v "grep" | grep -E "$rock_mon|$rock_engine" | wc -l`
if [ $var -ne 2 ]; then
	echo 'backup' > $file
	killall keepalived
    #echo "$rock_mon engine down !"
	exit 1
else
    exit 0
fi

