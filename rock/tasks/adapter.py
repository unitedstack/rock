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


from nova.i18n import _, _LW, _LE

import taskflows as rock_taskflow

class CommonAdapter(object):

    def evacuate_vm(self,uuid,on_shared_storage):
        """ Evacuate a server from a failed host to a new one.
        """

        rock_taskflow.run_evacuate_taskflow(uuid,on_shared_storage)
        return evacuate_vm('8277fb3f-d506-455a-b285-0c62b3848f4b','True')





