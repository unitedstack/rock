from actions import NovaAction
from flow_utils import BaseTask


class ServerEvacuate(BaseTask, NovaAction):
    def execute(self, server, on_shared_storage=True):

        success = False
        n_client = self._get_client()
        try:
            (response, dictionary) = n_client.servers.evacuate(
                on_shared_storage=on_shared_storage,
                server=server)

            if response is None:
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
            "reason": res_message,
        }
