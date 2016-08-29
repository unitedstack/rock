#!/usr/bin/env bash

date >> /usr/local/bin/d.txt


rock_mon="/usr/bin/rock-mon"
rock_engine="/usr/bin/rock-engine"

var=`ps -ef | grep -v grep | grep $rock_mon`
if [ -z "$var" ]; then
    #echo 'yes'
    rock-mon > /dev/null 2>&1 &
fi

var=`ps -ef | grep -v grep | grep $rock_engine`
if [ -z "$var" ]; then
    #echo 'yes'
    rock-engine > /dev/null 2>&1 &
fi



