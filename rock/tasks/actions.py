from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client
import os
import json
from oslo_config import cfg

CONF = cfg.CONF

env_opts = [ 
    cfg.StrOpt('USERNAME',
              default='admin'),
    cfg.IntOpt('VERSION',
              default=2.0),
    cfg.StrOpt('PASSWORD',
              default='1q2w3e4r'),
    cfg.StrOpt('AUTH_URL',
               default='http://lb.103.hatest.ustack.in:35357/v3'),
    cfg.StrOpt('PROJECT_NAME',
              default='openstack'),
    cfg.StrOpt('PROJECT_DOMAIN_ID',
              default='default'),
    cfg.StrOpt('USER_DOMAIN_ID',
              default='default'),
    cfg.StrOpt('host'),
]


cfg.CONF.register_opts(env_opts)


class NovaAction():
    def _get_client(self):

        auth=identity.Password(username=CONF.USERNAME,
                              password=CONF.PASSWORD,
                              project_name=CONF.PROJECT_NAME,
                              auth_url=CONF.AUTH_URL,
                              project_domain_id=CONF.PROJECT_DOMAIN_ID,
                              user_domain_id=CONF.USER_DOMAIN_ID)

        sess = session.Session(auth=auth,verify=False)

        n_client = client.Client(CONF.VERSION,session=sess)

        return n_client


class IPMIAction():
    global data

    with open('tasks/target.json', 'r') as f:
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

    def power_cycle(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power cycle'
        os.system(cmd)

    def power_reset(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power reset'
        os.system(cmd)

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._ip) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power status'
        os.system(cmd)


