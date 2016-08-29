#!/usr/bin/env bash

rock_mon="/usr/bin/rock-mon"

var=`ps -ef | grep -v grep | grep $rock_mon`
if [ -n "$var" ]; then
    var=`echo $var | awk '{print $2}'`
    #echo $var 
    kill $var
fi

