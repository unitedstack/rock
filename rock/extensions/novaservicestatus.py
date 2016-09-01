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

from keystoneauth1 import identity
from keystoneauth1 import session
from novaclient import client
import eventlet
from eventlet.queue import LightQueue
from oslo_config import cfg

from rock import extension_manager
from rock.db import api as db_api
from rock.db.sqlalchemy.model_nova_service import ModelNovaService


CONF = cfg.CONF

openstack_credential_group = cfg.OptGroup(
        'openstack_credential',
        title='Openstack administrator credential.')

openstack_credential_opts = [
        cfg.StrOpt('username',
                    default='admin'),
        cfg.StrOpt('user_domain_name',
                    default='default'),
        cfg.StrOpt('nova_client_version',
                    default=2.0),
        cfg.StrOpt('password',
                    default=None),
        cfg.StrOpt('auth_url',
                    default=None),
        cfg.StrOpt('project_name',
                    default='admin'),
        cfg.StrOpt('project_domain_id',
                    default='default')
        ]

CONF.register_group(openstack_credential_group)
CONF.register_opts(openstack_credential_opts, openstack_credential_group)


class Novaservicestatus(extension_manager.ExtensionDescriptor):

    def __init__(self):
        super(Novaservicestatus, self).__init__()
        self.queue = LightQueue(100)
        self.pool = eventlet.GreenPool(4)

    @classmethod
    def get_name(cls):
        return 'Nova Compute Service Status'

    @classmethod
    def get_alias(cls):
        return 'nova-service-status'

    @classmethod
    def get_description(cls):
        return "Status of nova compute for a specified host"

    def periodic_task(self):
        self.pool.spawn(self.producer)
        self.pool.spawn(self.consumer)

    def _get_client(self):
        """Get a nova client"""

        auth=identity.Password(
            auth_url=CONF.openstack_credential.auth_url,
            username=CONF.openstack_credential.username,
            password=CONF.openstack_credential.password,
            user_domain_name=CONF.openstack_credential.user_domain_name,
            project_domain_name=CONF.openstack_credential.project_domain_id,
            project_name=CONF.openstack_credential.project_name
        )
        sess = session.Session(auth=auth,verify=False)
        nova_client_version = CONF.openstack_credential.nova_client_version
        n_client = client.Client(nova_client_version, session=sess)
        return n_client

    def producer(self):
        n_client = self._get_client()
        services = n_client.services.list()
        result = {}
        for service in services:
            if service.binary == u'nova-compute':
                result[service.host] = {'state': service.state,
                                        'status': service.status}
        self.queue.put(result, block=False, timeout=1)

    def consumer(self):
        result = self.queue.get(block=False, timeout=1)
        objs = []
        for k,v in result.items():
            objs.append(
                    ModelNovaService(
                        target=str(k),
                        result=True if v['state'] == u'up' else False,
                        service_state=True if v['state'] == u'up' else False,
                        service_status=True \
                                if v['status'] == u'enabled' else False
                    )
            )
        db_api.save_all(objs)
