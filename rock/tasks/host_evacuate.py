from flow_utils import BaseTask
from actions import NovaAction
from  server_evacuate import ServerEvacuateTask
import logging

class HostEvacuateTask(BaseTask,NovaAction):

    def execute(self, host):
        n_client = self._get_client()

        evacuated_host = host
        evacuable_servers = n_client.servers.list(
            search_opts={'host':evacuated_host,
                         'all_tenants':1})

        evacuated_servers = list()
        for server in evacuable_servers:
            logging.debug("Processing %s" % server)
            if hasattr(server,'id'):
                response = ServerEvacuateTask().execute(server.id,True)
                if response['accepted']:
                    logging.info("Evacuated %s from %s: %s" %
                                 (response["uuid"], evacuated_host, response["reason"]))
                    evacuated_servers.append(server)
                else:
                    logging.error("Evacuation of %s on %s failed: %s" %
                                  (response["uuid"], evacuated_host, response["reason"]))
                time.sleep(2)
            else:
                logging.error("Could not evacuate instance: %s" % server.to_dict())


