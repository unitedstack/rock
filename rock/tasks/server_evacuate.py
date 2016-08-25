from flow_utils import BaseTask
from actions import NovaAction 
import logging


class ServerEvacuate(BaseTask,NovaAction):

    def execute(self, on_shared_storage, server):

        success = False
        error_message = ""
        n_client = self._get_client()
        try:
            logging.info("Resurrecting instance: %s" % server)
            (response, dictionary) = n_client.servers.evacuate(
                on_shared_storage=on_shared_storage,
                server = server)

            if response == None:
                res_message = "No response while evacuating instance"
            elif response.status_code == 200:
                success = True
                res_message = response.reason
            else:
                res_message = response.reason
        
        except Exception as e:
            res_message = "Error while evacuating instance: %s" % e

        return {
            "uuid": server,
            "accepted": success,
            "reason": error_message,
        }

    def revert():
        pass
