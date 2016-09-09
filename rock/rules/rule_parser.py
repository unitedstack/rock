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
import datetime
import uuid

from oslo_log import log as logging
from oslo_utils import importutils
from oslo_utils import timeutils

from rock.db import api as db_api
from rock.rules import rule_utils
from rock.tasks.manager import run_flow


LOG = logging.getLogger(__name__)


def data_get_by_obj_time(obj_name, delta):
    model_name = 'model_' + obj_name
    model = importutils.import_class(
        'rock.db.sqlalchemy.%s.%s' %
        (model_name, rule_utils.underline_to_camel(model_name)))
    timedelta = datetime.timedelta(seconds=delta)
    return db_api.get_period_records(model,
                                     timeutils.utcnow()-timedelta,
                                     end_time=timeutils.utcnow(),
                                     sort_key='created_at')


ACTION_ALIAS = {
    'power_operation': 'rock.tasks.power_manager.PowerManager',
    'host_evacuate': 'rock.tasks.host_evacuate.HostEvacuate',
    'host_disable': 'rock.tasks.host_disable.HostDisable'
}


class RuleParser(object):
    def __init__(self, rule):
        if isinstance(rule, basestring):
            self.rule = json.loads(rule)
        else:
            self.rule = rule

        self.raw_data = {}
        self.target_data = {}
        self.l1_data = {}
        self.l2_data = {}
        self.all_data = {}

    def calculate(self):
        LOG.info("Starting collect data.")
        self._collect_data()
        LOG.info("Got target data %s", self.target_data)
        l2_result = self._rule_mapping_per_target()
        LOG.info("Got l1 data %s", self.l1_data)
        LOG.info("Got l2 result %s", l2_result)
        if l2_result:
            self._action()

    def _collect_data(self):
        funcs = self.Functions()
        splited_raw_data = {}
        # raw_data organized by data_model.
        # {"data_model": [list_of_all_target_resources]}
        for key, value in self.rule["collect_data"].items():
            rule = copy.deepcopy(value['data'])
            # self.raw_data[key] = self._calculate(rule, funcs)
            splited_raw_data[key] = {}

        # splited_raw_data organized by data_model first, then target.
        # {"data_model": {"target": [list_of_single_target_resources]}}
        for key, value in self.raw_data.items():
            for item in value:
                if not splited_raw_data[key].get(item['target']):
                    splited_raw_data[key][item['target']] = [item]
                else:
                    splited_raw_data[key][item['target']].append(item)

        # target_data organized by target first, then data_model, and each
        # data_model show calc_result.
        # {'target': {'data_model': {'last_piece','judge_result'}
        for key, value in self.rule["collect_data"].items():
            for target, target_data in splited_raw_data[key].items():
                if not self.target_data.get(target):
                    self.target_data[target] = {}
                self.target_data[target][key] = {}
                judge_rule = value["judge"] + [target_data]
                self.target_data[target][key]['judge_result'] = \
                    self._calculate(judge_rule, funcs)
                self.target_data[target][key].update(target_data[0])

    def _rule_mapping_per_target(self):

        def _replace_variate(target, rule):
            for posi, value in enumerate(rule):
                if isinstance(value, unicode) and value.startswith('$'):
                    dict_args = value[1:].split('.')
                    rule[posi] = self.target_data[target][dict_args[0]]
                    dict_args.pop(0)
                    while dict_args:
                        rule[posi] = rule[posi][dict_args[0]]
                        dict_args.pop(0)
                elif isinstance(value, list):
                    _replace_variate(target, value)

        funcs = self.Functions()

        for target, data in self.target_data.items():
            l1_rule = copy.deepcopy(self.rule['l1_rule'])
            _replace_variate(target, l1_rule)
            self.l1_data[target] = \
                {'l1_result': self._calculate(l1_rule, funcs)}

        l2_rule = copy.deepcopy(self.rule['l2_rule'])
        l2_rule = self._replace_rule_parameter(l2_rule)
        return self._calculate(l2_rule, funcs)

    def _action(self):
        for target in self.l1_data:
            if not self.l1_data[target]:
                tasks = []
                task_uuid = uuid.uuid4()
                task_name = 'task-' + task_uuid
                LOG.info("Triggered action on %s.", target)
                store_spec = {'task_uuid': task_uuid,
                              'target': target}
                for task in self.rule['action']:
                    class_name = ACTION_ALIAS[task[0]]
                    task_cls = importutils.import_class(class_name)
                    tasks.append(task_cls())
                    for input_params in task[1:]:
                        input_kv = input_params.spilt(':')
                        store_spec[input_kv[0]] = input_kv[1]

                run_flow(task_name, store_spec, tasks)

    def _calculate(self, rule, funcs):
        def _recurse_calc(arg):
            if isinstance(arg, list) and isinstance(arg[0], unicode) \
                    and arg[0].startswith('%') and arg[0] != '%map':
                return self._calculate(arg, funcs)
            elif isinstance(arg, list)and arg[0] == '%map':
                ret = {}
                for k, v in arg[1].items():
                    map_rule = self._replace_map_para(arg[2], arg[1], k)
                    ret[k] = {}
                    ret[k]['map_result'] = self._calculate(map_rule, funcs)
                return ret
            else:
                return arg

        r = map(_recurse_calc, rule)
        r[0] = self.Functions.ALIAS.get(r[0]) or r[0]
        func = getattr(funcs, r[0])
        return func(*r[1:])

    def _replace_rule_parameter(self, rule):
        if not isinstance(rule, list):
            return

        def _recurse_replace(arg):
            if isinstance(arg, list) and isinstance(arg[0], unicode) \
                    and arg[0].startswith('%'):
                return self._replace_rule_parameter(arg)
            elif isinstance(arg, unicode) and arg.startswith('$'):
                args = arg[1:].split('.')
                ret = getattr(self, args[0])
                args.pop(0)
                while args:
                    ret = ret[args[0]]
                    args.pop(0)
                return ret
            else:
                return arg

        r = map(_recurse_replace, rule)
        return r

    def _replace_map_para(self, map_rule, para_dict, target):

        def _recurse_replace(arg):
            if isinstance(arg, list) and isinstance(arg[0], unicode) \
                    and arg[0].startswith('%'):
                return self._replace_map_para(arg, para_dict, target)
            elif isinstance(arg, unicode) and arg.startswith('map.'):
                map_para_list = arg.split('.')
                map_para_list.pop(0)
                ret = para_dict[target][map_para_list[0]]
                map_para_list.pop(0)
                while map_para_list:
                    ret = ret[map_para_list[0]]
                    map_para_list.pop(0)
                return ret
            else:
                return arg
        r = map(_recurse_replace, map_rule)
        return r

    class Functions(object):

        ALIAS = {
            '%==': 'eq',
            '%<=': 'lt_or_eq',
            '%and': '_and',
            '%or': '_or',
            '%not': '_not',
            '%get_by_time': 'get_data_by_time',
            '%false_end_count_lt': 'false_end_count_lt',
            '%count': 'count',
            '%map': '_map'
        }

        def eq(self, *args):
            return args[0] == args[1]

        def lt_or_eq(self, *args):
            return args[0] <= args[1]

        def _and(self, *args):
            return all(args)

        def _or(self, *args):
            return any(args)

        def _not(self, *args):
            return not args[0]

        def get_data_by_time(self, *args):
            return data_get_by_obj_time(args[0], args[1])

        def false_end_count_lt(self, *args):
            boundary = int(args[0])
            count = 0
            for item in args[1]:
                if item['result'] in [False, 'false', 'False']:
                    count += 1
                else:
                    break
            return count < boundary

        def count(self, *args):
            if args[2] in [False, 'false', 'False']:
                count_type = False
            elif args[2] in [True, 'true', 'True']:
                count_type = True
            else:
                return len(args[1])
            count = 0
            for k, v in args[0].items():
                if v.get(args[1]) == count_type:
                    count += 1
            return count
