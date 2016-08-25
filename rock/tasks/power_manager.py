from actions import IPMIAction
from flow_utils import BaseTask
import logging

class PowerManager(BaseTask,IPMIAction):

    def execute(self,ip):
        
        try:
            info = IPMIAction(ip)
            info.power_off()
            result = info.power_status()
            if result == 0:
                logging.info("Success to power off host that ip is %s" % ip)
            return True
        except Exception as e:
            return False


