# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

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
