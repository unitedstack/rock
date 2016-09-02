from flow_utils import BaseTask
from actions import NovaAction
from actions import IPMIAction
from  server_evacuate import ServerEvacuate
from oslo_log import log as logging
import time


LOG = logging.getLogger(__name__)

class HostEvacuate(BaseTask,NovaAction,IPMIAction):

    def execute(self, target):
        host = target
        n_client = self._get_client()

        evacuated_host = host
        evacuable_servers = n_client.servers.list(
            search_opts={'host':evacuated_host,
                         'all_tenants':1})
        evacuated_servers = list()
        for server in evacuable_servers:
            LOG.debug("Processing %s" % server)
            if hasattr(server,'id'):
                response = ServerEvacuate().execute(server.id,True)
                if response['accepted']:
                    LOG.info("Evacuated %s from %s: %s" %
                                 (response["uuid"], evacuated_host, response["reason"]))
                    evacuated_servers.append(server.id)
                else:
                    LOG.error("Evacuation of %s on %s failed: %s" %
                                  (response["uuid"], evacuated_host, response["reason"]))
            else:
                LOG.error("Could not evacuate instance: %s" % server.to_dict())
        
        evacuated = list()
        for ID in evacuated_servers:
           evacuated.append(n_client.servers.get(ID))
           
        flag = False
        while not flag:
            flag = True
            for server in evacuated:
                server.task_state = getattr(server,'OS-EXT-STS:task_state')
                if server.task_state != None:
                    flag = False
                    time.sleep(3)
                    break
           
        for server in evacuated:
            LOG.debug("checking the status of server: %s" % server.id)
            server.host = getattr(server,'OS-EXT-SRV-ATTR:host')
            if server.host != unicode(host):
                LOG.info("Evacuate server %s successfully" % server.id)
            else:
                LOG.info("Evacuate server %s failed, its status is %s" % (server.id, server.status))

        
