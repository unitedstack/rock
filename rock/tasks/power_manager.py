from actions import IPMIAction
from flow_utils import BaseTask
from oslo_log import log as logging
import time

LOG = logging.getLogger(__name__)


class PowerManager(BaseTask, IPMIAction):
    default_provides = "host_power_off_result"

    def execute(self, target):

        try:
            LOG.info("Trying to power off %s" % target)
            ipmi = IPMIAction(target)
            status_code = ipmi.power_off()
            if status_code != 0:
                LOG.warning("Failed to power off host %s" % target)
                return False
            LOG.info("Waiting 30s...")
            time.sleep(30)
            code, output = ipmi.power_status()
            if code == 0 and output.split(' ')[-1] == 'off':
                LOG.info("Power status of %s: %s" % (target, output))
                LOG.info("Success to power off host %s" % target)
                return True
            else:
                LOG.warning(
                    "Failed to power off host %s due to %s" % (target, output))
                return False
        except Exception as e:
            LOG.warning(
                "Failed to power off host %s due to %s" % (target, e.message))
            return False
