from ipmi import IPMITool
from flow_utils import BaseTask
import logging

class HostPowerTask(BaseTask,IPMITool):

    def execute(self, target, username, password):
        
        try:
            info = IPMITool(target, username, password)
            info.power_off()
            result = info.power_status()
            if result == 'Chassis Power is off':
                logging.info("Success to power off host that ip is %s" % target)
            return True
        except Exception as e:
            return False


