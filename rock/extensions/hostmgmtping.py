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

import eventlet
import commands
from eventlet.queue import LightQueue

from oslo_config import cfg

from rock import extension_manager
from rock.db.sqlalchemy.model_ping import ModelPing

host_mgmt_ping_opts_group = cfg.OptGroup(name='host_mgmt_ping',
    title="Opts about host management IP ping delay")

host_mgmt_ping_opts = [
    cfg.ListOpt('target_addresses',
                default=["127.0.0.1"],
                help="IP address or hostname of target, hostname should be" +
                "pingable directly."),
]

CONF = cfg.CONF
CONF.register_group(host_mgmt_ping_opts_group)
CONF.register_opts(host_mgmt_ping_opts, host_mgmt_ping_opts_group)


class Hostmgmtping(extension_manager.ExtensionDescriptor):
    """Ping to management IP of host extension."""

    def __init__(self):
        super(Hostmgmtping, self).__init__()
        self.queue = LightQueue(100)
        self.pool = eventlet.GreenPool(2)
        self.targets = CONF.host_mgmt_ping.target_addresses

    @classmethod
    def get_name(cls):
        return "Host Management IP Ping"

    @classmethod
    def get_alias(cls):
        return "host-mgmt-ping"

    @classmethod
    def get_description(cls):
        return "Delay of ping to management IP of host."

    def periodic_task(self):
        self.pool.spawn(self.producer)
        self.pool.spawn(self.consumer)

    def producer(self):
        result = {}
        for target in self.targets:
            cmd = "ping -c 3 -t 3 -W 1 -i 0.3 %s" % target
            output = commands.getoutput(cmd)
            result[target] = output.split('\n')[-1].split('/')[-3]
        self.queue.put(result, block=False, timeout=3)

    def consumer(self):
        result = self.queue.get(block=False, timeout=3)
        ping_objs = self.get_models(result)
        db_api.save_all(ping_objs)

    def get_models(self,result):
        objs = []
        for key in result:
            obj = ModelPing(target=key, delay=result[key])
            objs.append(obj)
        return objs
