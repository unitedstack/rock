#!/bin/bash

ha_status='/usr/local/bin/ha_status'
if [ ! -f $ha_status ];then
	touch $ha_status
fi

case $1 in
"master")
	source '/usr/local/bin/start.sh'
	echo 'master' > $ha_status
	;;
"backup")
	echo 'backup' > $ha_status
	source '/usr/local/bin/kill.sh'
	;;
*)
	echo '*' > $ha_status
	;;
esac
