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

from oslo_config import cfg

from rock.extension_manager import ExtensionDescriptor
from rock.db import api as db_api
from rock.db.sqlalchemy.model_ping import ModelPing

host_mgmt_ping_opts_group = cfg.OptGroup(
    name='host_mgmt_ping', title="Opts about host management IP ping delay")

host_mgmt_ping_opts = [
    cfg.ListOpt(
        'target_addresses',
        default=["127.0.0.1"],
        help="IP address or hostname of target, hostname should be" +
        "pingable directly."),
    cfg.DictOpt(
        'ip_hostname_map', default={}, help="IP addresses map to hostname"),
]

CONF = cfg.CONF
CONF.register_group(host_mgmt_ping_opts_group)
CONF.register_opts(host_mgmt_ping_opts, host_mgmt_ping_opts_group)


class Hostmgmtping(ExtensionDescriptor):
    """Ping to management IP of host extension."""

    def __init__(self):
        super(Hostmgmtping, self).__init__()
        self.targets = CONF.host_mgmt_ping.target_addresses
        self.targets_hostname = CONF.host_mgmt_ping.ip_hostname_map

    @classmethod
    def get_name(cls):
        return "Host Management IP Ping"

    @classmethod
    def get_alias(cls):
        return "host-mgmt-ping"

    @classmethod
    def get_description(cls):
        return "Delay of ping to management IP of host."

    @ExtensionDescriptor.period_decorator(10)
    def periodic_task(self):
        data = {}
        for target in self.targets:
            # Send 3 packets one time and each packet timeout is 3000ms,
            # interval between 3 packets is 0.3s, and the ping process
            # will only wait for 3s for all
            cmd = "ping -c 3 -t 4 -W 3 -i 0.3 %s" % target
            status, output = commands.getstatusoutput(cmd)
            if status == 0:
                data[self.targets_hostname[target]] = \
                    output.split('\n')[-1].split('/')[-3]
            else:
                data[self.targets_hostname[target]] = '9999'
        ping_objs = self.get_models(data)
        db_api.save_all(ping_objs)

    def get_models(self, data):
        objs = []
        for key in data:
            obj = ModelPing(
                target=key,
                delay=data[key],
                result=True if float(data[key]) < 3 else False)
            objs.append(obj)
        return objs
