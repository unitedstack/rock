from actions import IPMIAction
from flow_utils import BaseTask
from oslo_log import log as logging
import time
import json

LOG = logging.getLogger(__name__)

class PowerManager(BaseTask,IPMIAction):

    def execute(self,target):
        
        try:
            info = IPMIAction(target)
            info.power_off()
            time.sleep(5)
            result = info.power_status()

            if result == None:
                LOG.info("Success to power off host %s" % target)
                with open('/etc/rock/target.json','r+') as f:
                    data = json.load(f)
                    if data.get(target, None) is not None:
                        data.pop(target)
                with open('/etc/rock/target.json','w+') as f:
                    json.dump(data,f)

            return True
        except Exception as e:
            return False

