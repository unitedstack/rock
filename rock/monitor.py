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

import os

from oslo_config import cfg
from oslo_utils import importutils

from oslo_log import log as logging


def prepare_log():
    default_log_dir = '/var/log/rock'
    default_log_file = 'rock-mon.log'
    conf = cfg.CONF
    logging.register_options(conf)
    conf(default_config_files=['/etc/rock/rock.ini'])
    conf.set_default('log_dir', conf.get('log_dir', None) or default_log_dir)
    try:
        log_file = conf.get('rock_mon_log_file')
        conf.set_default('log_file', log_file)
    except cfg.NoSuchOptError:
        conf.set_default('log_file', default_log_file)
    if not os.path.exists(conf.log_dir):
        os.mkdir(conf.log_dir)
    logging.setup(conf, "rock-mon")


def main(manager='rock.extension_manager.ExtensionManager'):
    prepare_log()
    log = logging.getLogger(__name__)
    log.info('Start rock monitor.')
    mgr_class = importutils.import_class(manager)
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    ext_mgr = mgr_class(file_dir + '/extensions')
    ext_mgr.start_collect_data()


if __name__ == '__main__':
    main()
