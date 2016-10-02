from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client
import requests

username = 'admin'
user_domain_id = 'default'
password = 'dffcb42eb3a0c8795cbea277'
auth_url = 'http://10.0.100.37:35357/v3'
project_name = 'openstack'
project_domain_id = 'default'

auth = identity.Password(username=username,
                         password=password,
                         project_name=project_name,
                         auth_url=auth_url,
                         project_domain_id=project_domain_id,
                         user_domain_id=user_domain_id)

sess = session.Session(auth=auth, verify=False)
nova_client_version = '2.0'

n_client = client.Client(nova_client_version, session=sess)

instance = n_client.servers.list()

print instance

json_payload = {
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                    "name": "admin",
                    "domain": {
                        "id": "default"
                    },
                    "password": "dffcb42eb3a0c8795cbea277"
                }
            }
        }
    }
}

import json

headers = {'content-type': 'application/json', 'accept': 'application/json'}

resp = requests.post('http://10.0.100.37:35357/v3'+'/auth/tokens',
                     data=json.dumps(json_payload), headers=headers)
print resp.headers.get('X-Subject-Token', None)

import itertools
from oslo_config import cfg
obj = cfg.BoolOpt('test')
print getattr(obj, 'name')
d ={}
d.pop('ss', True)

s = 'sdll'


def f(*args, **kwargs):
    print kwargs

f(kwargs=2, name=None)