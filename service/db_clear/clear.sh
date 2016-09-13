#!/bin/bash

month=`date -u -d "+%Y-%m-%d %H:%M:%S"`
tables='/root/lsj/tables.txt'

tables=`cat $tables`
db=rock_history
for x in $tables
do
   echo "table: $x"
   mysql $db -e "delete from $x where created_at < '$month'" 2>>/root/lsj/log.txt
done
