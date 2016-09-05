#!/usr/bin/env bash

rock_mon="/bin/rock-mon"
rock_engine="/bin/rock-engine"

var=`ps -ef | grep -v grep | grep $rock_mon`
if [ -n "$var" ]; then
    var=`echo $var | awk '{print $2}'`
    #echo $var 
    kill $var
fi

var=`ps -ef | grep -v grep | grep $rock_engine`
if [ -n "$var" ]; then
    var=`echo $var | awk '{print $2}'`
    #echo $var
    kill $var
fi



