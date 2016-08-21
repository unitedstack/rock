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

from taskflow import task
import taskflow.engines
from taskflow import engines
from taskflow.patterns import linear_flow as lf
from flow_utils import BaseTask
from actions import NovaAction,IPMIAction
from oslo_log import log as logging
from nova.i18n import _, _LW, _LE 

LOG = logging.getLogger(__name__)

class EvacuateTask(BaseTask,NovaAction):

    def execute(self,uuid,on_shared_storage,evacuate):
        n_client = self._get_client()
        LOG.debug('%s.execute', self.__class__.__name__)

        if self.evacuate:
            print n_client.servers.evacuate(uuid,on_shared_storage)

    def revert(self,result,uuid,on_shared_storage,evacuate):
        method_name = '%s.revert' % self.__class__.__name__

        LOG.warning(_LW('%(method_name)s: '
                       'evacuate vm %(uuid) is failed'),
                    {'method_name': method_name,
                     'uuid': uuid})

class IPMITask(BaseTask,IPMIAction):

    def execuate(self):
        pass

    def revert(self):
        pass


def run_evacuate_taskflow(uuid,on_shared_storage):
    flow_name =  'evacuate_vm'
    store_spec = {'uuid': uuid,
                  'on_shared_storage': True,
                 }

    work_flow = lf.Flow(flow_name)
    work_flow.add(EvacuateTask())
    engine = taskflow.engines.load(work_flow,store=store_spec)
    engine.run()

def sure_IPMI_taskflow():
    pass