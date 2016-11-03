import json
import commands

from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client
from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class NovaAction(object):
    @staticmethod
    def _get_client():
        """Get a nova client"""

        auth = identity.Password(
            username=CONF.openstack_credential.username,
            password=CONF.openstack_credential.password,
            project_name=CONF.openstack_credential.project_name,
            auth_url=CONF.openstack_credential.auth_url,
            project_domain_id=CONF.openstack_credential.project_domain_id,
            user_domain_id=CONF.openstack_credential.user_domain_id)

        sess = session.Session(auth=auth, verify=False)
        nova_client_version = CONF.openstack_credential.nova_client_version

        n_client = client.Client(nova_client_version, session=sess)

        return n_client


class IPMIAction(object):
    def __init__(self, hostname):
        with open('/etc/rock/target.json', 'r') as f:
            data = json.load(f)
        self._ip = data[hostname]['ip']
        self._username = data[hostname]['username']
        self._password = data[hostname]['password']

    def power_on(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power on'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning(
                "Can not power on %s due to %s" % (self._ip, e.message))
            return 1
        return status_code

    def power_off(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power off'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning(
                "Can not power off %s due to %s" % (self._ip, e.message))
            return 1
        return status_code

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' + str(self._ip) + ' -U ' \
              + str(self._username) + ' -P ' + str(
            self._password) + ' chassis power status'
        try:
            status_code, output = commands.getstatusoutput(cmd)
        except Exception as e:
            LOG.warning("Can not get power status of %s due to %s" % (
                self._ip, e.message))
            return 1
        return status_code, output
