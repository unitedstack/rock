# -*- coding: utf-8 -*-

from oslo_config import cfg
import MySQLdb
from sql_statement import *

CONF = cfg.CONF
database_group = cfg.OptGroup(
        'database',
        title='database parameters')

database_opt = cfg.StrOpt(
    'connection',
    help='Database connection string',
)

if getattr(CONF, 'database', None) is None:
    CONF.register_group(database_group)
    CONF.register_opt(database_opt, database_group)
else:
    if getattr(CONF.database, 'connection', None) is None:
        CONF.register_opt(database_opt, CONF.database)

CONF(default_config_files=['/etc/rock/rock.ini'])
conn_str = CONF.database.connection
conn_str_dict = conn_str.split('/')[-2]
user = conn_str_dict.split(':')[0]
conn_str_dict_1 = conn_str_dict.split(':')[1]
passwd = conn_str_dict_1.split('@')[0]
host = conn_str_dict_1.split('@')[1]

conn = MySQLdb.connect(host=host,
                       user=user,
                       passwd=passwd,
                       db='rock',
                       charset='utf8')
cursor = conn.cursor()

table = 'flowdetails'
cursor.execute(get_last(table))

flowdetails = cursor.fetchone()
