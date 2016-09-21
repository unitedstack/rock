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


def register_conf(conf):
    host_mgmt_ping_group = \
        cfg.OptGroup(name='host_mgmt_ping',
                     title="Opts about host management IP ping delay")
    host_mgmt_ping_opts = [
        cfg.DictOpt(
            'ip_hostname_map', default={},
            help="IP addresses map to hostname"),
    ]

    host_evacuate_group = cfg.OptGroup(
        name='host_evacuate', title='Opts for host evacuate')
    host_evacuate_opts = [
        cfg.IntOpt(
            'check_times',
            default=6,
            help="how many times to check the evacuated server's status"),
        cfg.IntOpt(
            'check_interval', default=15, help='check interval')
    ]

    conf.register_group(host_evacuate_group)
    conf.register_opts(host_evacuate_opts, host_evacuate_group)

    if getattr(conf, 'host_mgmt_ping', None) is None:
        conf.register_group(host_mgmt_ping_group)
        conf.register_opts(host_mgmt_ping_opts, host_mgmt_ping_group)
    else:
        if getattr(conf.host_mgmt_ping, 'ip_hostname_map', None) is None:
            conf.register_opts(host_mgmt_ping_opts, host_mgmt_ping_group)


register_conf(CONF)


class HostEvacuate(BaseTask, NovaAction):

    default_provides = ('message_body', 'host_evacuate_result')

    def execute(self, target, taskflow_uuid, host_power_off_result):
        n_client = self._get_client()
        servers, servers_id = self.get_servers(n_client, target)

        # Force down nova compute of target
        # self.force_down_nova_compute(n_client, host)

        # 1. Check nova compute state of target
        nova_compute_state = self.check_nova_compute_state(n_client, target)
        if not nova_compute_state or not host_power_off_result:
            return self.get_evacuate_results(n_client, servers_id, target,
                                             taskflow_uuid), False

        # 2. Evacuate servers on the target
        self.evacuate_servers(servers)

        # 3. Check evacuate status, while all servers successfully evacuated,
        # it will return, otherwise it will wait check_times * time_delta.
        self.check_evacuate_status(
            n_client,
            servers_id,
            target,
            check_times=CONF.host_evacuate.check_times,
            time_delta=CONF.host_evacuate.check_interval)

        return self.get_evacuate_results(n_client, servers_id, target,
                                         taskflow_uuid), True

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
            LOG.debug("Request to evacute server: %s" % server.id)
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

    def get_evacuate_results(self, n_client, vms_uuid, vm_origin_host,
                             taskflow_uuid):
        results = []
        for vm_id in vms_uuid:
            vm = n_client.servers.get(vm_id)
            vm_task_state = getattr(vm, 'OS-EXT-STS:task_state', None)
            vm_host = getattr(vm, 'OS-EXT-SRV-ATTR:host', None)

            if (vm_task_state is None) and \
                    (vm_host != unicode(vm_origin_host)):

                results.append(
                    self.make_vm_evacuate_result(vm, True, taskflow_uuid))

                LOG.info("Successfully evacuated server: %s, origin_host: %s"
                         ", current_host: %s" %
                         (vm.id, vm_origin_host, vm_host))

            else:
                results.append(
                    self.make_vm_evacuate_result(vm, False, taskflow_uuid))

                LOG.warning(
                    "Failed evacuate server: %s, origin_host: %s, "
                    "current_host: %s, vm_task_state: %s" %
                    (vm.id, vm_origin_host, vm_host, vm_task_state))
        return results

    def make_vm_evacuate_result(self, vm, success, taskflow_uuid):
        target = str(getattr(vm, 'OS-EXT-SRV-ATTR:host'))
        severity = '2'
        if success:
            summary = 'vm ' + str(vm.id) + '|' + self.get_vm_ip(vm) + ' ' + \
                      target + '|' + self.get_target_ip(target) + ' HA SUCCESS'
        else:
            summary = 'vm ' + str(vm.id) + '|' + self.get_vm_ip(vm) + ' ' + \
                      target + '|' + self.get_target_ip(target) + ' HA FAILED'
        last_occurrence = datetime.datetime.utcnow().\
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
        for ip, hostname in CONF.host_mgmt_ping.ip_hostname_map.items():
            if target == hostname:
                return ip
        return 'none'
