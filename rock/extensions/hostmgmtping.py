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

import commands
import threading

from oslo_config import cfg

from rock.db import api as db_api
from rock.db.sqlalchemy.model_ping import ModelPing
from rock.extension_manager import ExtensionDescriptor

CONF = cfg.CONF
DATA_LIST = []
LOCK = threading.RLock()


class PingThread(threading.Thread):
    def __init__(self, host_name, host_ip_map):
        super(PingThread, self).__init__(name=host_name)
        self.host_name = host_name
        self.host_ip_map = host_ip_map

    def run(self):
        global DATA_LIST
        data = dict()
        data['target'] = self.host_name
        data['result'] = False
        for ip_name, ip in self.host_ip_map.items():
            # Send total 3 packets to the ip address and the interval between
            # each packet is 0.3s. And wait for each response of the packet
            # at most 1s.
            if ip_name == 'm':
                db_filed_1 = 'management_ip_result'
                db_filed_2 = 'management_ip_delay'
            elif ip_name == 't':
                db_filed_1 = 'tunnel_ip_result'
                db_filed_2 = 'tunnel_ip_delay'
            else:
                db_filed_1 = 'storage_ip_result'
                db_filed_2 = 'storage_ip_delay'
            cmd = "ping -c 3 -W 1 -i 0.3 %s" % ip
            status, output = commands.getstatusoutput(cmd)
            if status == 0:
                data[db_filed_2] = output.split('\n')[-1].split('/')[-3]
                if float(data[db_filed_2]) < 1.0:
                    data[db_filed_1] = True
                    data['result'] = True
                else:
                    data[db_filed_1] = False
            else:
                data[db_filed_2] = '9999'
                data[db_filed_1] = False
        ping_obj = ModelPing(**data)
        LOCK.acquire()
        DATA_LIST.append(ping_obj)
        LOCK.release()


class Hostmgmtping(ExtensionDescriptor):
    """Ping to management IP of host extension."""

    def __init__(self):
        super(Hostmgmtping, self).__init__()
        self.compute_hosts = CONF.host_mgmt_ping.compute_hosts
        self.management_network_ip = CONF.host_mgmt_ping.management_network_ip
        self.tunnel_network_ip = CONF.host_mgmt_ping.tunnel_network_ip
        self.storage_network_ip = CONF.host_mgmt_ping.storage_network_ip
        self.host_ip_map = self.map_host_and_ips()

    def map_host_and_ips(self):
        i = 0
        mapping = {}
        for host in self.compute_hosts:
            mapping[host] = {}
            if len(self.management_network_ip) > 0:
                mapping[host]['m'] = self.management_network_ip[i]
            if len(self.tunnel_network_ip) > 0:
                mapping[host]['t'] = self.tunnel_network_ip[i]
            if len(self.storage_network_ip) > 0:
                mapping[host]['s'] = self.storage_network_ip[i]
            i += 1
        return mapping

    @classmethod
    def get_name(cls):
        return "Host Management IP Ping"

    @classmethod
    def get_alias(cls):
        return "host-mgmt-ping"

    @classmethod
    def get_description(cls):
        return "Delay of ping to management IP of host."

    @staticmethod
    def save_data():
        global DATA_LIST
        LOCK.acquire()
        db_api.save_all(DATA_LIST)
        del DATA_LIST[:]
        LOCK.release()

    @ExtensionDescriptor.period_decorator(10)
    def periodic_task(self):
        current_thread_list = threading.enumerate()
        current_thread_name_list = list()
        current_thread_name_list.append(thread.name
                                        for thread in current_thread_list)
        for host_name, host_ip_map in self.host_ip_map.items():
            if host_name in current_thread_name_list:
                continue
            pt = PingThread(host_name, host_ip_map)
            pt.start()
        t = threading.Thread(target=self.save_data,
                             name='Plugin-Ping-Data-Save')
        t.start()
