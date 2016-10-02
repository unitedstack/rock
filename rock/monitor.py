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

from rock import utils
from oslo_utils import importutils

from oslo_log import log as logging


def main(manager='rock.extension_manager.ExtensionManager'):
    utils.register_all_options()
    utils.prepare_log(service_name='rock-mon')
    log = logging.getLogger(__name__)
    log.info('Start rock monitor.')
    mgr_class = importutils.import_class(manager)
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    ext_mgr = mgr_class(file_dir + '/extensions')
    ext_mgr.start_collect_data()


if __name__ == '__main__':
    main()
