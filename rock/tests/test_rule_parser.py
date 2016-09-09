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
import json

from rock.rules import rule_parser


test_rule = """
{
    "rule_name": "host_down",
    "collect_data": {
        "service_result": {"data": ["%get_by_time", "nova_service", 300],
                           "judge": ["%false_end_count_lt", 2]},
        "ping_result": {"data": ["%get_by_time", "ping", 300],
                        "judge": ["%false_end_count_lt", 2]}
    },
    "l1_rule": [
        "%or",
        "$service_result.judge_result",
        "$ping_result.judge_result"
    ],
    "l2_rule": [
        "%and",
        ["%==", ["%count", "$l1_data", "l1_result", false], 1],
        [
            "%<=",
            [
                "%count",
                [
                    "%map",
                    "$target_data",
                    [
                        "%and",
                        [
                            "%not",
                            "map.service_result.service_status"
                        ],
                        [
                            "%==",
                            "map.service_result.disabled_reason",
                            "host_down_disable"
                        ]
                    ]
                ],
                "map_result",
                true
            ],
        2]
    ],
    "action": {
        "filters": [
            [
                "%==",
                "$service_result.service_status",
                true
            ]
        ],
        "tasks": [
            ["power_operation"],
            ["host_evacuate"],
            ["host_disable", "disabled_reason:host_down_disable"],
            ["message_report", "message_destination:/queue/eventQueue"]
        ]
    }
}
"""

service_status = [
    {u"target": u"a", u"time": u"00:06", u"result": False, u"service_status": True, u"disabled_reason": u"host_down_disable"},
    {u"target": u"b", u"time": u"00:05", u"result": False, u"service_status": True, u"disabled_reason": u"some_other_reason"},
    {u"target": u"c", u"time": u"00:04", u"result": True, u"service_status": False, u"disabled_reason": u""},
    {u"target": u"a", u"time": u"00:03", u"result": False, u"service_status": False, u"disabled_reason": u""},
    {u"target": u"b", u"time": u"00:02", u"result": True, u"service_status": False, u"disabled_reason": u""},
    {u"target": u"c", u"time": u"00:01", u"result": True, u"service_status": True, u"disabled_reason": u"host_down_disable"},
]

ping_status = service_status

test_parser = rule_parser.RuleParser(json.loads(test_rule))
test_parser.raw_data["service_result"] = service_status
test_parser.raw_data["ping_result"] = service_status
test_parser.calculate()
print(test_parser.l1_data)
print(test_parser.l2_data)
