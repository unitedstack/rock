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

import manager
import taskflow.engines
from taskflow import task
from taskflow import engines
from taskflow.patterns import linear_flow as lf
from flow_utils import BaseTask
from actions import NovaAction
from oslo_log import log as logging
from nova.i18n import _, _LW, _LE 
from taskflow.types import failure
LOG = logging.getLogger(__name__)

class EvacuateTask(BaseTask,NovaAction):

    def execute(self,uuid,on_shared_storage,evacuate):
        n_client = self._get_client()
        LOG.debug('%s.evacuate', self.__class__.__name__)

        if evacuate:
            print n_client.servers.evacuate(server=uuid,on_shared_storage=on_shared_storage)

#    def revert(self,result,uuid,on_shared_storage):
#        method_name = '%s.revert' % self.__class__.__name__
#
#        LOG.warning(_LW('%(method_name)s: '
#                       'evacuate vm %(uuid)s is failed'),
#                    {'method_name': method_name,
#                     'uuid': uuid})

class HostEvacuateTask(BaseTask,NovaAction):

    def execute(self,server):
        n_client = self._get_client()
        LOG.debug('%s.host.evacuate',self.__class__.__name__)

        if server:
            print n_client.host_evacuate.do_host_evacuate(server=server)

    def revert(self,result,server):
        pass

class NovaServiceTask(BaseTask,NovaAction):
    def execute(self):
        n_client = self._get_client()
        LOG.debug('%s.service.list',self.__class__.__name__)

        print n_client.services.list()


def run_evacuate_taskflow(uuid,on_shared_storage,evacuate):
    flow_name =  'evacuate_vm'
    store_spec = {'uuid': uuid,
                  'on_shared_storage': True,
                  'evacuate':True
                 }

    manager.run_flow(flow_name,store_spec,EvacuateTask())

def run_host_evacuate_taskflow(server,on_shared_storage):
    flow_name = 'host_evacuate'
    store_spec = {'server':server,
                  'on_shared_storage':on_shared_storage
                 }
    manager.run_flow(flow_name,store_spec,HostEvacuateTask())

def nova_service_taskflow():
    
    flow_name = 'service_list'
    store_spec = None

    manager.run_flow(flow_name,store_spec,NovaServiceTask()) 
