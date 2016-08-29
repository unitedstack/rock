from flow_utils import BaseTask
from actions import NovaAction
from  server_evacuate import ServerEvacuate
import logging
import time

class HostEvacuate(BaseTask,NovaAction):

    def execute(self, target):
        host = target
        n_client = self._get_client()
    
        logging.info("checking the state of nova compute service on the host %s" % host)
        services = n_client.services.list()
        flag = False
        while not flag:
            for s in services:
                if s.host == unicode(host) and s.binary == u'nova-compute' and s.state == u'down':
                    flag = True
                    print "<Service:%s, Host:%s, State:%s>" % (s.binary,s.host,s.state)
                    break
                else:
                    flag = False
                    time.sleep(5)

        evacuated_host = host
        evacuable_servers = n_client.servers.list(
            search_opts={'host':evacuated_host,
                         'all_tenants':1})

        evacuated_servers = list()
        for server in evacuable_servers:
            logging.debug("Processing %s" % server)
            if hasattr(server,'id'):
                response = ServerEvacuate().execute(server.id,True)
                if response['accepted']:
                    logging.info("Evacuated %s from %s: %s" %
                                 (response["uuid"], evacuated_host, response["reason"]))
                    evacuated_servers.append(server)
                else:
                    logging.error("Evacuation of %s on %s failed: %s" %
                                  (response["uuid"], evacuated_host, response["reason"]))
            else:
                logging.error("Could not evacuate instance: %s" % server.to_dict())

    def revert():
        pass

