#!/bin/bash

path="/usr/local/bin"
month=`date -u  "+%Y-%m-%d %H:%M:%S"`
tables="$path/tables.txt"

tables=`cat $tables`
db=rock_history
for x in $tables
do
   # echo "table: $x"
   mysql $db -e "delete from $x where created_at < '$month'" 2>>$path/log.txt
done
