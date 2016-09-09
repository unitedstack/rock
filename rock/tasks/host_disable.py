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

from actions import NovaAction
from flow_utils import BaseTask

LOG = logging.getLogger(__name__)


class HostDisable(BaseTask, NovaAction):

    def execute(self, target, disable_reason):
        n_client = self._get_client()

        response = n_client.services.disable_log_reason(
            host=target,
            binary='nova-compute',
            reason=disable_reason
        )
        LOG.info("Host %s disabled for reason %s.", target, disable_reason)

        if response['accepted']:
            LOG.info("Host %s disable successfully.", target)
        else:
            LOG.error("Host %s disable failed, reason %s.", target, response)
