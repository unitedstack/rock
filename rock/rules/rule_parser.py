# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy
import json

from oslo_log import log as logging


LOG = logging.getLogger(__name__)


def data_get_by_obj(obj_name, filters):
    pass


class RuleParser(object):
    def __init__(self, rule):
        if isinstance(rule, basestring):
            self.rule = json.loads(rule)
        else:
            self.rule = rule

        self.raw_data = {}
        self.target_data = {}
        self.l1_data = {}

    def calculate(self):
        self._collect_data()
        l2_result = self._rule_mapping_per_target()
        if l2_result:
            self._action()

    def _collect_data(self):
        funcs = self.Functions()
        splited_raw_data = {}
        for key, value in self.rule["collect_data"].items():
            #self.raw_data[key] = self._calculate(value['data'], funcs)
            splited_raw_data[key] = {}

        for key, value in self.raw_data.items():
            for item in value:
                if not splited_raw_data[key].get(item['target']):
                    splited_raw_data[key][item['target']] = [item]
                else:
                    splited_raw_data[key][item['target']].append(item)

        for key, value in self.rule["collect_data"].items():
            for target, target_data in splited_raw_data[key].items():
                if not self.target_data.get(target):
                    self.target_data[target] = {}
                judge_rule = value["judge"] + [target_data]
                self.target_data[target][key] = \
                    self._calculate(
                        judge_rule, funcs)

    def _rule_mapping_per_target(self):

        def _replace_variate(target, rule):
            for posi, value in enumerate(rule):
                if isinstance(value, str) and value.startswith('$'):
                    rule[posi] = self.target_data[target][value[1:]]
                elif isinstance(value, list):
                    _replace_variate(target, value)

        funcs = self.Functions()

        for target, data in self.target_data.items():
            l1_rule = copy.deepcopy(self.rule['l1_rule'])
            _replace_variate(target, l1_rule)
            self.l1_data[target] = self._calculate(l1_rule, funcs)

        def _add_l1_result(rule):
            rule.append(self.l1_data)
            for i in rule:
                if isinstance(i, list):
                    i.append(self.l1_data)
                    _add_l1_result(i)

        l2_rule = self.rule['l2_rule']
        _add_l1_result(l2_rule)
        return self._calculate(l2_rule, funcs)

    def _action(self):
        print('do some action')

    def _calculate(self, rule, funcs):
        def _recurse_calc(arg):
            if isinstance(arg, list) and isinstance(arg[0], str) \
                    and arg[0].startswith('%'):
                return self._calculate(arg, funcs)
            else:
                return arg

        r = map(_recurse_calc, rule)
        r[0] = self.Functions.ALIAS.get(r[0]) or r[0]
        func = getattr(funcs, r[0])
        return func(*r[1:])

    class Functions(object):

        ALIAS = {
            '%==': 'eq',
            '%and': '_and',
            '%get_by_time': 'get_data_by_time',
            '%false_end_count_lt': 'false_end_count_lt',
            '%count': 'count'
        }

        def eq(self, *args):
            return args[0] == args[1]

        def _and(self, *args):
            return all(args)

        def get_data_by_time(self, *args):
            filters = {}
            return data_get_by_obj(args[0], filters)

        def false_end_count_lt(self, *args):
            boundary = int(args[0])
            count = 0
            for item in args[1]:
                if item['result'] in [False, 'false', 'False']:
                    count += 1
            return count < boundary

        def count(self, *args):
            if args[0] in [False, 'false', 'False']:
                count_type = False
            elif args[0] in [True, 'true', 'True']:
                count_type = True
            else:
                return len(args[1])
            count = 0
            for k, v in args[1].items():
                if v == count_type:
                    count += 1
            return count
