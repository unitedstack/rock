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

import json
import os

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import loopingcall

from rock.rules.rule_parser import RuleParser

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class RuleManager(object):
    """
    Load all cases and run them.
    """

    def __init__(self, path):
        LOG.info('Initializing rule manager.')
        self.path = path
        self.cases = []
        self.periodic_task = None
        self._load_all_cases()

    def _load_all_cases(self):
        for path in self.path.split(':'):
            if os.path.exists(path):
                self._get_all_cases_recursively(path)
            else:
                LOG.error("Extension path '%s' doesn't exist!", path)

    def after_start(self):
        self.periodic_task = \
                loopingcall.FixedIntervalLoopingCall(self.calculate_task)
        self.periodic_task.start(interval=CONF.check_cases_interval)
        self.periodic_task.wait()

    def calculate_task(self):
        for case in self.cases:
            if isinstance(case, dict):
                self._calculate(case)

    def _get_all_cases_recursively(self, path):
        for dir_path, dir_names, file_names in os.walk(path):
            for file_name in file_names:
                with open(os.path.join(dir_path, file_name), 'r') as f:
                    try:
                        self.cases.append(json.loads(f.read()))
                        LOG.info("Case %s loaded", file_name)
                    except Exception as e:
                        LOG.warning(
                            'Load case error, error %s, case_file %s.' %
                            (e.message, file_name))

    def _calculate(self, rule_detail):
        LOG.info("Calculating %s", rule_detail)
        parser = RuleParser(rule_detail)
        parser.calculate()
