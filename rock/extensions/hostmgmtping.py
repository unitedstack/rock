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

from oslo_service import loopingcall

from rock import extension_mgr
from rock import gather
from rock.db import models


class HostMgmtPing(extensions.ExtensionDescriptor, models.HostMgmtPing):
    """Ping to management IP of host extension."""

    def __init__(self):
        super(HostMgmtPing, self).__init__()

    @classmethod
    def get_name(cls):
        return "Host Management Ping"

    @classmethod
    def get_alias(cls):
        return "host-mgmt-ping"

    @classmethod
    def get_description(cls):
        return "Delay of ping to management IP of host."

    def periodic_task(self,)