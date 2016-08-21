from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client

from oslo_config import cfg

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
]

cfg.CONF.register_opts(env_opts)


class NovaAction():
    def _get_client(self):

        auth=identity.Password(username=USERNAME,
                              password=PASSWORD,
                              project_name=PROJECT_NAME,
                              auth_url=AUTH_URL,
                              project_domain_id=PROJECT_DOMAIN_ID,
                              user_domain_id=USER_DOMAIN_ID)

        sess = session.Session(auth=auth,verify=False)

        n_client = client.Client(VERSION,session=sess)

        return n_client


class IPMIAction():
    pass
