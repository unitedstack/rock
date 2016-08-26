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

from oslo_utils import importutils
from oslo_config import cfg
from oslo_service import loopingcall

import eventlet

def register_opts(conf):
	conf(default_config_files=['/etc/rock/rock.ini'])

def main(manager='rock.extension_manager.ExtensionManager'):
    register_opts(cfg.CONF)
    mgr_class = importutils.import_class(manager)
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    ext_mgr = mgr_class(file_dir+'/extensions')
    p = loopingcall.FixedIntervalLoopingCall(ext_mgr.report_state_loop)
    p.start(interval=4)
    ext_mgr.after_start()
    p.wait()

if __name__ == '__main__':
    main()
