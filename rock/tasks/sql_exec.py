# -*- coding: utf-8 -*-

from oslo_config import cfg
import MySQLdb
from sql_statement import *

CONF = cfg.CONF
database_group = cfg.OptGroup(
        'database',
        title='database infomation.')

database_opts = [
    cfg.StrOpt('host',
               default='127.0.0.1'),
    cfg.StrOpt('user',
               default='root'),
    cfg.StrOpt('passwd',
               default='admin'),
]

if getattr(CONF, 'database', None) is None:
    CONF.register_group(database_group)
else:
    if getattr(CONF.database, 'host', None) is None \
            and getattr(CONF.database, 'user', None) is None \
            and getattr(CONF.database, 'passwd', None) is None:
        CONF.register_opts(database_opts, database_group)

CONF(default_config_files=['/etc/rock/rock.ini'])

conn = MySQLdb.connect(host=CONF.database.host,
                       user=CONF.database.user,
                       passwd=CONF.database.passwd,
                       db='rock',
                       charset='utf8')
cursor = conn.cursor()

table = 'flowdetails'
cursor.execute(get_last(table))

flowdetails = cursor.fetchone()