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


def register_opts(conf):
    conf(default_config_files=['rock.ini'])


def main(manager='rock.rules.rule_manager.RuleManager'):
    register_opts(cfg.CONF)
    mgr_class = importutils.import_class(manager)
    mgr = mgr_class('cases')
    mgr.after_start()

if __name__ == '__main__':
    main()
