# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
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

"""Utilities and helper functions."""

import os

from oslo_log import log
from oslo_config import cfg
from rock import exceptions
from rock import opts

CONF = cfg.CONF

HA_DISABLE_REASON = 'ha_disable_reason'


def prepare_log(service_name):
    log.register_options(CONF)
    CONF(default_config_files=['/etc/rock/rock.ini'])
    CONF.set_default('log_dir', '/var/log/rock')
    rock_mon_log_file = getattr(CONF, 'rock_mon_log_file', 'rock-mon.log')
    rock_engine_log_file = getattr(CONF, 'rock_engine_log_file',
                                   'rock-engine.log')
    if service_name == 'rock-mon':
        CONF.set_override('log_file', override=rock_mon_log_file)
    elif service_name == 'rock-engine':
        CONF.set_override('log_file', override=rock_engine_log_file)
    else:
        raise exceptions.InvalidService(service_name=service_name)

    if not os.path.exists(CONF.log_dir):
        os.mkdir(CONF.log_dir)
    log.setup(CONF, service_name)


def register_all_options():
    """Register all options for rock
    """
    for option in opts.list_opts():
        CONF.register_opts(opts=option[1], group=option[0])
