from actions import IPMIAction
from flow_utils import BaseTask
from oslo_log import log as logging
import time

LOG = logging.getLogger(__name__)

class PowerManager(BaseTask,IPMIAction):

    def execute(self,target):
        
        try:
            info = IPMIAction(target)
            info.power_off()
            result = info.power_status()
            if result == 0:
                LOG.info("Success to power off host %s" % target)
            return True
        except Exception as e:
            return False


