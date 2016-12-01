#!/usr/bin/bash
# This script is used to drop data in rock_history.

timestamp=$(date -u "+%Y-%m-%d %H:%M:%S")
database_connection=$(cat /etc/rock/rock.ini | grep "^ *connection*")
database_tables=("ping" "nova_service")

# Get database connection information
database_user=$(echo ${database_connection} | awk -F ':' '{print $2}' | awk -F '/' '{print $3}')
database_pass=$(echo ${database_connection} | awk -F ':' '{print $3}' | awk -F '@' '{print $1}')
database_host=$(echo ${database_connection} | awk -F '@' '{print $2}' | awk -F '/' '{print $1}')
database_name=$(echo ${database_connection} | awk -F '/' '{print $NF}' | awk -F '?' '{print $1}')

for table in ${database_tables[@]}
do
    mysql -u${database_user} -p${database_pass} -h${database_host} -D${database_name}_history -e \
        "delete from ${table} where created_at < '${timestamp}'"
done
