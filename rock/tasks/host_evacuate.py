# -*- coding: utf-8 -*-
from flow_utils import BaseTask
from actions import NovaAction
from server_evacuate import ServerEvacuate
from oslo_log import log as logging
import time
import datetime


LOG = logging.getLogger(__name__)


class HostEvacuate(BaseTask, NovaAction):

    default_provides = 'message_body'

    def execute(self, target, taskflow_uuid):
        host = target
        n_client = self._get_client()
        evacuated_host = host

        evacuable_servers = n_client.servers.list(
                        search_opts={
                            'host': evacuated_host,
                            'all_tenants': 1
                        }
        )

        evacuated_servers_id = []

        for server in evacuable_servers:
            LOG.debug("Request to evacute server: %s" % server.id)
            evacuated_servers_id.append(server.id)

            if hasattr(server, 'id'):
                response = ServerEvacuate().execute(server.id,True)
                if response['accepted']:
                    LOG.info("Request to evacuate server: %s accepted" %
                             server.id)
                else:
                    LOG.error("Request to evacuate server: %s failed" %
                              server.id)
            else:
                LOG.error("Could not evacuate instance: %s" %
                          server.to_dict())

        time.sleep(90)

        return self.get_evacuate_results(n_client,
                                         evacuated_servers_id,
                                         evacuated_host,
                                         taskflow_uuid)

    def get_evacuate_results(self, n_client, vm_uuids,
                             vm_origin_host, taskflow_uuid):
        results = []
        for vm_id in vm_uuids:
            vm = n_client.servers.get(vm_id)
            vm_task_state = getattr(vm, 'OS-EXT-STS:task_state', None)
            vm_host = getattr(vm, 'OS-EXT-SRV-ATTR:host', None)

            if (vm_task_state is None) and \
                     (vm_host != unicode(vm_origin_host)):

                results.append(
                    self.make_vm_evacuate_result(vm, True,
                                                 taskflow_uuid))

                LOG.info("Successfully evacuate server: %s, origin_host: %s"
                         ", current_host: %s"
                         % (vm.id, vm_origin_host, vm_host))

            else:
                results.append(
                    self.make_vm_evacuate_result(vm, False,
                                                 taskflow_uuid))

                LOG.warning("Failed evacuate server: %s, origin_host: %s"
                            "vm_task_state: %s"
                            % (vm.id, vm_origin_host, vm_task_state))
        return results

    def make_vm_evacuate_result(self, vm, success, taskflow_uuid):
        severity = '2'
        if success:
            summary = 'vm ' + str(vm.id) + '/' + self.get_vm_ip(vm) + \
                      ' ' + str(vm.hostId) + '/' + \
                      str(getattr(vm, 'OS-EXT-SRV-ATTR:host')) + ' HA成功'
        else:
            summary = 'vm ' + str(vm.id) + '/' + self.get_vm_ip(vm) + \
                      ' ' + str(vm.hostId) + '/' + \
                      str(getattr(vm, 'OS-EXT-SRV-ATTR:host')) + ' HA失败'
        last_occurrence = datetime.datetime.utcnow(). \
                            strftime('%m/%d/%Y %H:%M:%S')
        status = 1
        source_id = 10
        # source_identifier =
        source_event_id = taskflow_uuid
        source_ci_name = str(vm.id)
        source_alert_key = 'ROCK_VM_HA'
        source_severity = 'INFO'

        single_result = {
                'Severity': severity,
                'Summary': summary,
                'LastOccurrence': last_occurrence,
                'Status': status,
                'SourceID': source_id,
                'SourceEventID': source_event_id,
                'SourceCIName': source_ci_name,
                'SourceAlertKey': source_alert_key,
                "SourceSeverity": source_severity
        }

        return single_result

    def get_vm_ip(self, vm):
        vm_ip = ''
        for k, v in vm.networks.items():
            for ip in v:
                vm_ip += str(ip)+','
        vm_ip.rstrip(',')
        return vm_ip