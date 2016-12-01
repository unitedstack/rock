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
from oslo_log import log as logging
from rock.tasks import flow_utils

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class HostEvacuate(flow_utils.BaseTask):
    default_provides = ('message_body', 'host_evacuate_result')

    def execute(self, target, taskflow_uuid, host_power_off_result):
        n_client = flow_utils.get_nova_client()
        servers, servers_id = self.get_servers(n_client, target)
        if len(servers) == 0:
            LOG.info("There is no active instance on host: %s, "
                     "no need to evacuate" % target)
            return [], True
        else:
            LOG.info("Instance(s) to evacuate: %s" % ' '.join(servers_id))
        message_generator = 'message_generator_for_' + CONF.message_report_to

        # Force down nova compute of target
        # self.force_down_nova_compute(n_client, host)

        # Check nova compute state of target
        nova_compute_state = self.check_nova_compute_state(n_client, target)

        if not nova_compute_state or not host_power_off_result:
            if not nova_compute_state:
                LOG.warning("Failed to perform evacuation of compute host: %s "
                            "due to nova compute service is still up" % target)
            if not host_power_off_result:
                LOG.warning("Failed to perform evacuation of compute host: %s "
                            "due to can't state power status of this host"
                            % target)
            evacuate_result = self.get_evacuate_results(
                n_client, servers_id, target, taskflow_uuid,
                message_generator=message_generator)
            return evacuate_result[0], evacuate_result[2]

        """
        # Evacuate servers on the target
        self.evacuate_servers(servers, n_client)

        # Check evacuate status, while all servers successfully evacuated,
        # it will return, otherwise it will wait check_times * time_delta.
        self.check_evacuate_status(
            n_client, servers_id, target,
            check_times=CONF.host_evacuate.check_times,
            time_delta=CONF.host_evacuate.check_interval)
        """

        for server in servers:
            self.evacuate_servers([server], n_client)
            self.check_evacuate_status(
                n_client, [server.id], target,
                check_times=CONF.host_evacuate.check_times,
                time_delta=CONF.host_evacuate.check_interval)

        evacuate_result = self.get_evacuate_results(
            n_client, servers_id, target, taskflow_uuid,
            message_generator=message_generator)

        if not evacuate_result[2]:
            self.reset_state(n_client, evacuate_result[1])

        return evacuate_result[0], evacuate_result[2]

    @staticmethod
    def get_servers(n_client, host):
        """"Get all servers on the host which vm_state is active"""
        try:
            servers = n_client.servers.list(search_opts={
                'host': host,
                'all_tenants': 1,
                'status': 'active'
            })
        except Exception as err:
            LOG.warning("Can't get active servers on host %s due to %s"
                        % (host, err.message))
            return [], []
        servers_id = []
        for server in servers:
            servers_id.append(server.id)
        return servers, servers_id

    @staticmethod
    def evacuate_servers(servers, n_client):
        """Evacuate servers"""
        on_shared_storage = CONF.host_evacuate.on_shared_storage
        for server in servers:
            try:
                LOG.debug("Request to evacuate server: %s" % server.id)
                res = n_client.servers.evacuate(
                    server=server.id,
                    on_shared_storage=on_shared_storage)
                if res[0].status_code == 200:
                    LOG.info("Request to evacuate server %s accepted"
                             % server.id)
                else:
                    LOG.warning("Request to evacuate server %s failed due "
                                "to %s"
                                % (server.id, res[0].reason))
            except Exception as err:
                LOG.warning("Request to evacuate server %s failed due "
                            "to %s" % (server.id, err.message))

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
    def check_evacuate_status(n_client, vms_uuid, vm_origin_host,
                              check_times=6, time_delta=15):
        """Check the evacuate status

        Because this function is only designed for waiting some times to
        let nova compute service to perform evacuation. So, we only focus
        on the instance's vm_task to judge whether an instance was evacuated
        successfully. vm_state and vm_host here is not important!
        """
        LOG.info("Checking evacuate status. Check times: %s, check "
                 "interval: %ss." % (check_times, time_delta))
        continue_flag = True
        time.sleep(time_delta)
        for i in range(check_times - 1):
            if continue_flag:
                for vm_id in vms_uuid:
                    vm = n_client.servers.get(vm_id)
                    vm_task_state = getattr(vm, 'OS-EXT-STS:task_state', None)
                    if vm_task_state is not None:
                        time.sleep(time_delta)
                        continue_flag = True
                        break
                    continue_flag = False
            else:
                break

    @staticmethod
    def judge(instance, origin_host):
        """Decide whether evacuated success or not of a single instance

        Here we need decide which instance failed to evacuate precisely.
        1. If current_host != origin_host and vm_task is None, only this
           situation we consider it evacuated successfully. (no qa)
        2. Carefully, if current_host == origin_host but vm_task is not None,
           the instance may just in progress of evacuation, we mark it
           evacuated failed. There is some problem: if it is in progress of
           evacuation, but later it failed, we can't reset is state from
           'error' to 'active'. How to fixed it??
        3. If current_host != origin_host but vm_task is not None, we consider
           it evacuated successfully. (no qa)
        4. If current_host == origin_host and vm_task is None, we firmly
           consider it evacuated failed. (no qa)
        """
        task = getattr(instance, 'OS-EXT-STS:task_state', None)
        host = getattr(instance, 'OS-EXT-SRV-ATTR:host', None)
        state = getattr(instance, 'OS-EXT-STS:vm_state', None)
        if host != unicode(origin_host):
            # state == active, task == None
            # state == active, task != None
            # state == error, task == None ? need additional operations?
            # state == error, task != None ? need additional operations?
            LOG.info("Successfully evacuated server: %s, origin_host: %s"
                     ", current_host: %s, vm_task: %s, vm_state: %s" %
                     (instance.id, origin_host, host, task, state))
            return True, state
        else:
            LOG.warning("Failed evacuate server: %s, origin_host: %s, "
                        "current_host: %s, vm_task: %s, vm_state: %s"
                        % (instance.id, origin_host, host, task, state))
            LOG.warning("Mark server %s evacuated failed and "
                        "should be evacuated later" % instance.id)
            return False, state

    def get_evacuate_results(
            self, n_client, vms_uuid, vm_origin_host, taskflow_uuid,
            message_generator='message_generator_for_activemq'):
        """Get evacuate results and generate messages

        Before this method is executed, we have involved check_evacuate_status.
        We have waited enough time to perform evacuation.
        """

        messages = []
        failed_uuid_and_state = {}

        generator = getattr(self, message_generator, None)
        if generator is None:
            LOG.error("Invalid message generator: %s" % message_generator)
            for vm_id in vms_uuid:
                vm = n_client.servers.get(vm_id)
                res = self.judge(vm, vm_origin_host)
                if not res[0]:
                    failed_uuid_and_state[vm_id] = res[1]
            if len(failed_uuid_and_state) > 0:
                return messages, failed_uuid_and_state, False
            else:
                return messages, failed_uuid_and_state, True

        for vm_id in vms_uuid:
            vm = n_client.servers.get(vm_id)
            res = self.judge(vm, vm_origin_host)
            if res[0]:
                messages.append(generator(vm, True,
                                          taskflow_uuid=taskflow_uuid,
                                          origin_host=vm_origin_host))
            else:
                failed_uuid_and_state[vm_id] = res[1]
                messages.append(generator(vm, False,
                                          taskflow_uuid=taskflow_uuid,
                                          origin_host=vm_origin_host))
        if len(failed_uuid_and_state) > 0:
            return messages, failed_uuid_and_state, False
        else:
            return messages, failed_uuid_and_state, True

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

    @staticmethod
    def reset_state(n_client, failed_uuid_and_state):
        LOG.info("Stating reset state for servers we previously "
                 "collected which failed perform evacuation")
        for uuid, state in failed_uuid_and_state.items():
            if state != u'active':
                LOG.info("Reset state of %s from current state: "
                         "%s to origin state: active" % (uuid, state))
                n_client.servers.reset_state(uuid, 'active')
