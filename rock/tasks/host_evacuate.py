# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime
import json
import time

from oslo_config import cfg

from actions import NovaAction
from flow_utils import BaseTask
from oslo_log import log as logging
from server_evacuate import ServerEvacuate

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class HostEvacuate(BaseTask, NovaAction):
    default_provides = ('message_body', 'host_evacuate_result')

    def execute(self, target, taskflow_uuid, host_power_off_result):
        n_client = self._get_client()
        servers, servers_id = self.get_servers(n_client, target)
        message_generator = 'message_generator_for_' + CONF.message_report_to

        # Force down nova compute of target
        # self.force_down_nova_compute(n_client, host)

        # Check nova compute state of target
        nova_compute_state = self.check_nova_compute_state(n_client, target)
        if not nova_compute_state or not host_power_off_result:
            return self.get_evacuate_results(
                n_client, servers_id, target, taskflow_uuid,
                message_generator=message_generator), False

        # Evacuate servers on the target
        self.evacuate_servers(servers)

        # Check evacuate status, while all servers successfully evacuated,
        # it will return, otherwise it will wait check_times * time_delta.
        self.check_evacuate_status(
            n_client,
            servers_id,
            target,
            check_times=CONF.host_evacuate.check_times,
            time_delta=CONF.host_evacuate.check_interval)

        return self.get_evacuate_results(
            n_client, servers_id, target, taskflow_uuid,
            message_generator=message_generator), True

    @staticmethod
    def get_servers(n_client, host):
        servers = n_client.servers.list(search_opts={
            'host': host,
            'all_tenants': 1
        })
        servers_id = []
        for server in servers:
            servers_id.append(server.id)
        return servers, servers_id

    @staticmethod
    def evacuate_servers(servers):
        for server in servers:
            LOG.debug("Request to evacuate server: %s" % server.id)
            if hasattr(server, 'id'):
                response = ServerEvacuate().execute(server.id, True)
                if response['accepted']:
                    LOG.info("Request to evacuate server: %s accepted" %
                             server.id)
                else:
                    LOG.error("Request to evacuate server: %s failed" %
                              server.id)
            else:
                LOG.error("Could not evacuate instance: %s" % server.to_dict())

    @staticmethod
    def force_down_nova_compute(n_client, host):
        n_client.services.force_down(host=host, binary='nova-compute')

    @staticmethod
    def check_nova_compute_state(n_client, host, check_times=20, time_delta=5):
        LOG.info("Checking nova compute state of host %s , ensure it is"
                 " in state 'down'." % host)
        for t in range(check_times):
            nova_compute = n_client.services.list(
                host=host, binary='nova-compute')
            state = nova_compute[0].state
            if state == u'up':
                LOG.warning("Nova compute of host %s is up, waiting it"
                            " to down." % host)
                time.sleep(time_delta)
            else:
                LOG.info("Nova compute of host %s is down." % host)
                # If nova compute is down, return True
                return True
        # If nova compute is always up, return False
        return False

    @staticmethod
    def check_evacuate_status(n_client,
                              vms_uuid,
                              vm_origin_host,
                              check_times=6,
                              time_delta=15):
        LOG.info(
            "Checking evacuate status. Check times: %s, check interval: %ss." %
            (check_times, time_delta))
        continue_flag = True
        for i in range(check_times):
            if continue_flag:
                for vm_id in vms_uuid:
                    vm = n_client.servers.get(vm_id)
                    vm_task_state = getattr(vm, 'OS-EXT-STS:task_state', None)
                    vm_host = getattr(vm, 'OS-EXT-SRV-ATTR:host', None)

                    if (vm_task_state is not None) or \
                            (vm_host == unicode(vm_origin_host)):
                        time.sleep(time_delta)
                        continue_flag = True
                        break

                    continue_flag = False
            else:
                break

    def get_evacuate_results(
            self, n_client, vms_uuid,
            vm_origin_host, taskflow_uuid,
            message_generator='message_generator_for_activemq'):

        results = []
        generator = getattr(self, message_generator, None)
        if generator is None:
            LOG.error("Invalid message generator: %s" % message_generator)
            return []

        for vm_id in vms_uuid:
            vm = n_client.servers.get(vm_id)
            vm_task_state = getattr(vm, 'OS-EXT-STS:task_state', None)
            vm_host = getattr(vm, 'OS-EXT-SRV-ATTR:host', None)

            if (vm_task_state is None) and \
                    (vm_host != unicode(vm_origin_host)):

                results.append(generator(vm, True,
                                         taskflow_uuid=taskflow_uuid,
                                         origin_host=vm_origin_host))

                LOG.info("Successfully evacuated server: %s, origin_host: %s"
                         ", current_host: %s" %
                         (vm.id, vm_origin_host, vm_host))

            else:
                results.append(generator(vm, False,
                                         taskflow_uuid=taskflow_uuid,
                                         origin_host=vm_origin_host))

                LOG.warning(
                    "Failed evacuate server: %s, origin_host: %s, "
                    "current_host: %s, vm_task_state: %s" %
                    (vm.id, vm_origin_host, vm_host, vm_task_state))
        return results

    @staticmethod
    def message_generator_for_kiki(vm, success, **kwargs):
        """Generate message of single instance for kiki.

        :param vm: virtual machine instance.
        :param success: indicate evacuation status.
        :param kwargs: some extra arguments for specific generator.
        :return: dict.
        """
        instance_id = getattr(vm, 'id', 'null')
        instance_name = getattr(vm, 'name', 'null')
        project_id = getattr(vm, 'tenant_id', 'null')
        user_id = getattr(vm, 'user_id', 'null')
        instance_status = getattr(vm, 'status', 'null')
        availability_zone = getattr(vm, 'OS-EXT-AZ:availability_zone', 'null')
        created_at = getattr(vm, 'created', 'null')
        networks = getattr(vm, 'networks', 'null')
        power_state = getattr(vm, 'OS-EXT-STS:power_state', 'null')
        task_state = getattr(vm, 'OS-EXT-STS:task_state', 'null')
        origin_host = kwargs.get('origin_host')
        current_host = getattr(vm, 'OS-EXT-SRV-ATTR:host', 'null')
        timestamp = datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S')

        if success:
            evacuation = 'evacuated successfully.'
        else:
            evacuation = 'failed to evacuate.'

        summery = 'Instance: ' + instance_name + '(' + instance_id + ') ' + \
                  evacuation
        result = {
            'summary': summery,
            'timestamp': timestamp,
            'power_state': power_state,
            'task_state': task_state,
            'instance_status': instance_status,
            'instance_id': instance_id,
            'instance_name': instance_name,
            'user_id': user_id,
            'project_id': project_id,
            'origin_host': origin_host,
            'current_host': current_host,
            'availability_zone': availability_zone,
            'instance_created_at': created_at,
            'networks': networks
        }

        return result

    def message_generator_for_activemq(self, vm, success, **kwargs):
        target = str(getattr(vm, 'OS-EXT-SRV-ATTR:host'))
        taskflow_uuid = kwargs.get('taskflow_uuid', None)
        severity = '2'
        if success:
            summary = 'vm ' + str(vm.id) + '|' + self.get_vm_ip(vm) + ' ' + \
                      target + '|' + self.get_target_ip(target) + ' HA SUCCESS'
        else:
            summary = 'vm ' + str(vm.id) + '|' + self.get_vm_ip(vm) + ' ' + \
                      target + '|' + self.get_target_ip(target) + ' HA FAILED'
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
            'SourceSeverity': source_severity
        }

        return json.dumps(single_result)

    @staticmethod
    def get_vm_ip(vm):
        vm_ip = ''
        for k, v in vm.networks.items():
            for ip in v:
                vm_ip += str(ip) + ','
        ip = vm_ip.rstrip(',')
        return ip

    @staticmethod
    def get_target_ip(target):
        index = CONF.host_mgmt_ping.compute_hosts.index(target)
        if len(CONF.host_mgmt_ping.management_network_ip) > index:
            return CONF.host_mgmt_ping.management_network_ip[index]
        else:
            return None
