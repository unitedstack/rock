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
from rock.tasks import flow_utils

LOG = logging.getLogger(__name__)


class HostDisable(flow_utils.BaseTask):

    default_provides = "host_disable_result"

    def execute(self, target, disabled_reason, host_evacuate_result):
        if not host_evacuate_result:
            return False

        n_client = flow_utils.get_nova_client()

        response = n_client.services.disable_log_reason(
            host=target,
            binary='nova-compute',
            reason=disabled_reason
        )
        LOG.info("Host %s disabled for reason %s.", target, disabled_reason)

        if response.status == 'disabled':
            LOG.info("Host %s disabled successfully.", target)
            return True
        else:
            LOG.error("Host %s disabled failed, reason %s.", target, response)
            return False
