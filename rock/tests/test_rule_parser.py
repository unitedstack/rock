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

"""
test for rule parser.
testcase: host down
"""

"""
situation: what if nova service all down, bug ping only one down.
"""

from rock.tools import rule_parser

test_rule = {
    "rule_name": "host_down",
    "collect_data": {
        'service_result': {"data": ["%get_by_time", "service_list", 300],
                           "judge": ["%false_end_count_lt", 2]},
        'ping_result': {"data": ["%get_by_time", "ping_delay", 300],
                        "judge": ["%false_end_count_lt", 2]}
    },
    "l1_rule": [
        "%and",
        "$service_result",
        "$ping_result"
    ],
    "l2_rule": [
        "%==", ["%count", False], 1
    ],
    "action": [
        ["IPMI", "$target", "power_off"],
        ["evacuate", "$target"]
    ]
}

service_status = [
    {"target": "a", "time":"00:06", "result": False},
    {"target": "b", "time":"00:05", "result": False},
    {"target": "c", "time":"00:04", "result": True},
    {"target": "a", "time":"00:03", "result": False},
    {"target": "b", "time":"00:02", "result": True},
    {"target": "c", "time":"00:01", "result": True},
]

ping_status = service_status

test_parser = rule_parser.RuleParser(test_rule)
test_parser.raw_data["service_result"] = service_status
test_parser.raw_data["ping_result"] = service_status
test_parser.calculate()
print(test_parser.l1_data)
