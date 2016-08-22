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

from oslo_log import log as logging
import taskflow.engines
from taskflow.patterns import linear_flow
import flow_utils

LOG = logging.getLogger(__name__)


def run_flow(flow_name,store_spec,tasks):
    """Constructs and run a task flow.
    """

    task_flow = linear_flow.Flow(flow_name)

    task_flow.add(
        tasks
    )

    # Now load (but do not run) the flow using the provided initial data.
    flow_engine = taskflow.engines.load(task_flow,store_spec)

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        flow_engine.run()
        LOG.info("Volume created successfully.")
