# -*- coding: utf-8 -*-

from oslo_config import cfg
import MySQLdb
from sql_statement import *

CONF = cfg.CONF
conn_str = CONF.database.connection
conn_str_dict = conn_str.split('/')[-2]
db = conn_str.split('/')[-1].split('?')[0]
user = conn_str_dict.split(':')[0]
conn_str_dict_1 = conn_str_dict.split(':')[1]
passwd = conn_str_dict_1.split('@')[0]
host = conn_str_dict_1.split('@')[1]

conn = MySQLdb.connect(host=host,
                       user=user,
                       passwd=passwd,
                       db=db,
                       charset='utf8')
cursor = conn.cursor()

table = 'flowdetails'
cursor.execute(get_last(table))

flowdetails = cursor.fetchone()
