#!/bin/bash

path='/root/lsj'
today=`date -u  "+%Y-%m-%d %H:%M:%S"`
tables="$path/tables.txt"

#echo "backup today:$today" >> $path/log.txt
#date >> $path/log.txt

var=`cat $tables`
db=rock
for x in $var
do
    mysql $db -e "insert into ${db}_history.$x select * from $db.$x as t1  where t1.created_at < '$today'" 2>>$path/log.txt \
    && mysql $db -e "delete from $x where created_at < '$today'" 2>>$path/log.txt
done


