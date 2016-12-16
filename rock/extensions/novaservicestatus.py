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

from oslo_config import cfg
from oslo_log import log as logging

from keystoneauth1 import identity, session
from novaclient import client
from rock.extension_manager import ExtensionDescriptor
from rock.db import api as db_api
from rock.db.sqlalchemy.model_nova_service import ModelNovaService

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Novaservicestatus(ExtensionDescriptor):

    def __init__(self):
        super(Novaservicestatus, self).__init__()

    @classmethod
    def get_name(cls):
        return 'Nova Compute Service Status'

    @classmethod
    def get_alias(cls):
        return 'nova-service-status'

    @classmethod
    def get_description(cls):
        return "Status of nova compute for a specified host"

    @ExtensionDescriptor.period_decorator(10)
    def periodic_task(self):
        n_client = self._get_client()
        try:
            services = n_client.services.list()
        except Exception as err:
            LOG.error("NovaClientException:")
            LOG.error(*err.args)
            LOG.error(err.message)
            return
        data = {}
        for service in services:
            if service.binary == u'nova-compute':
                data[service.host] = {
                    'state': service.state,
                    'status': service.status,
                    'disabled_reason': service.disabled_reason
                }

        objs = []
        for k, v in data.items():
            if v['disabled_reason'] is not None:
                disabled_reason = str(v['disabled_reason'])
            else:
                disabled_reason = v['disabled_reason']
            objs.append(
                ModelNovaService(
                    target=str(k),
                    result=True if v['state'] == u'up' else False,
                    service_state=True if v['state'] == u'up' else False,
                    service_status=True
                    if v['status'] == u'enabled' else False,
                    disabled_reason=disabled_reason))
        db_api.save_all(objs)

    def _get_client(self):
        """Get a nova client"""

        auth = identity.Password(
            auth_url=CONF.openstack_credential.auth_url,
            username=CONF.openstack_credential.username,
            password=CONF.openstack_credential.password,
            user_domain_id=CONF.openstack_credential.user_domain_id,
            project_domain_name=CONF.openstack_credential.project_domain_id,
            project_name=CONF.openstack_credential.project_name)

        sess = session.Session(auth=auth, verify=False)
        nova_client_version = CONF.openstack_credential.nova_client_version
        n_client = client.Client(
            nova_client_version,
            session=sess,
            region_name=CONF.openstack_credential.region_name)
        return n_client
