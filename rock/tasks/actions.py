from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client
import os
import json
from oslo_config import cfg

CONF = cfg.CONF

openstack_credential_group = cfg.OptGroup(
        'openstack_credential',
        title='openstack administrator credential.')

openstack_credential_opts = [ 
    cfg.StrOpt('username',
              default='admin'),
    cfg.StrOpt('nova_client_version',
              default=2.0),
    cfg.StrOpt('password',
              default=None),
    cfg.StrOpt('auth_url',
               default=None),
    cfg.StrOpt('project_name',
              default=None),
    cfg.StrOpt('project_domain_id',
              default='default'),
    cfg.StrOpt('user_domain_name',
              default='default'),
    cfg.StrOpt('host'),
]

CONF.register_group(openstack_credential_group)
CONF.register_opts(openstack_credential_opts, openstack_credential_group)


class NovaAction():
    def _get_client(self):
        """Get a nova client"""

        auth=identity.Password(username=CONF.openstack_credential.username,
                              password=CONF.openstack_credential.password,
                              project_name=CONF.openstack_credential.project_name,
                              auth_url=CONF.openstack_credential.auth_url,
                              project_domain_id=CONF.openstack_credential.project_domain_id,
                              user_domain_id=CONF.openstack_credential.user_domain_name)

        sess = session.Session(auth=auth,verify=False)
        nova_client_version = CONF.openstack_credential.nova_client_version

        n_client = client.Client(nova_client_version,session=sess)

        return n_client


class IPMIAction():
    global data

    with open('/etc/rock/target.json', 'r') as f:
        data = json.load(f)

    def __init__(self,hostname):
        self._ip = data[hostname]['ip']
        self._username = data[hostname]['username']
        self._password = data[hostname]['password']

    def power_on(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power on'
        os.system(cmd)

    def power_off(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power off'
        os.system(cmd)

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power status'
        os.system(cmd)


