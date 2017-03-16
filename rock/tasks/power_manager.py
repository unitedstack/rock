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

import time
import json
import commands

from flow_utils import BaseTask
from oslo_log import log as logging
from oslo_config import cfg

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class PowerManager(BaseTask):
    default_provides = "host_power_off_result"

    def execute(self, target):

        if CONF.ipmi.use_ipmi:
            try:
                LOG.info("Trying to power off %s" % target)
                ipmi = IPMIAction(target)
                status_code, output = ipmi.power_off()
                if status_code != 0:
                    # Some problems could happen when execute 'power off'
                    # command, But the power of the host could be already off.
                    # So, we could not return False here.
                    LOG.warning("Failed to execute ipmi 'power off' command of"
                                " host: %s, status_code: %s, command_output: "
                                "%s" % (target, status_code, output))
                    # return False
                LOG.info("Waiting 10s...")
                time.sleep(10)
                code, out = ipmi.power_status()
                if code == 0 and out.split(' ')[-1] == 'off':
                    LOG.info("Power status of %s: %s" % (target, out))
                    LOG.info("Success to power off host %s" % target)
                    return True
                else:
                    LOG.warning(
                        "Failed to power off host %s due to %s"
                        % (target, output))
                    return False
            except Exception as e:
                LOG.warning(
                    "Failed to power off host %s due to %s"
                    % (target, e.message))
                return False
        else:
            LOG.warning("Skipping power off compute host: %s, due to "
                        "'use_ipmi' option in rock.ini configured as fasle"
                        % target)
            return True


class IPMIAction(object):
    def __init__(self, hostname):
        with open('/etc/rock/target.json', 'r') as f:
            data = json.load(f)
        self._ip = data[hostname]['ip']
        self._username = data[hostname]['username']
        self._password = data[hostname]['password']

    def power_on(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power on'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning(
                "Can not power on %s due to %s" % (self._ip, e.message))
            return 1, e.message
        return status_code, output

    def power_off(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power off'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning(
                "Can not power off %s due to %s" % (self._ip, e.message))
            return 1, e.message
        return status_code, output

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power status'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning("Can not get power status of %s due to %s" % (
                self._ip, e.message))
            return 1, ' '
        return status_code, output
