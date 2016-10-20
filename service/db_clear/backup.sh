#!/usr/bin/bash
# This shell script is used to backup rock to rock_history, executed once a day

timestamp=$(date -u "+%Y-%m-%d %H:%M:%S")
database_connection=$(cat /etc/rock/rock.ini | grep "^ *connection*")
database_tables=("ping" "nova_service")

# Get database connection information
database_user=$(echo ${database_connection} | awk -F ':' '{print $2}' | awk -F '/' '{print $3}')
database_pass=$(echo ${database_connection} | awk -F ':' '{print $3}' | awk -F '@' '{print $1}')
database_host=$(echo ${database_connection} | awk -F '@' '{print $2}' | awk -F '/' '{print $1}')
database_name=$(echo ${database_connection} | awk -F '/' '{print $NF}' | awk -F '?' '{print $1}')

# Backup rock to rock_history
for table in ${database_tables[@]}
do
    mysql -u${database_user} -p${database_pass} -h${database_host} -e \
        "insert into ${database_name}_history.${table} select * from ${database_name}.${table} as t1 where t1.create < '${timestamp}'" \
    && mysql -u${database_user} -p${database_pass} -h${database_host} -e \
        "delete from ${database_name}.${table} where created_at < '${timestamp}'"
done
