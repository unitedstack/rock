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

from oslo_utils import importutils
from oslo_config import cfg
from oslo_log import log as logging


def prepare_log():
    DEFAULT_LOG_DIR = '/var/log/rock'
    DEFAULT_LOG_FILE = 'rock-engine.log'
    CONF = cfg.CONF
    logging.register_options(CONF)
    CONF(default_config_files=['/etc/rock/rock.ini'])
    CONF.set_default('log_dir', CONF.get('log_dir', None) or DEFAULT_LOG_DIR)
    try:
        log_file = CONF.get('rock_engine_log_file')
        CONF.set_default('log_file', log_file)
    except cfg.NoSuchOptError:
        CONF.set_default('log_file', DEFAULT_LOG_FILE)
    logging.setup(CONF, "rock-mon")

def main(manager='rock.rules.rule_manager.RuleManager'):
    prepare_log()
    LOG = logging.getLogger(__name__)
    LOG.info('Start rock engine')
    mgr_class = importutils.import_class(manager)
    mgr = mgr_class('cases')
    mgr.after_start()

if __name__ == '__main__':
    main()
