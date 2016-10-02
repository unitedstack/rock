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

import json

from oslo_config import cfg
from flow_utils import BaseTask
from oslo_log import log
import requests

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class MessageReportKiki(BaseTask):
    def execute(self, message_body):
        mail_api_endpoint = CONF.kiki.mail_api_endpoint
        mail_address = CONF.kiki.mail_address
        mail_content = json.dumps(message_body)
        mail_subject = 'Compute host HA operation'
        http_headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': get_token()
        }

        for address in mail_address:
            data = {
                "to": address,
                "subject": mail_subject,
                "content": mail_content
            }
            try:
                requests.post(mail_api_endpoint,
                              data=json.dumps(data),
                              headers=http_headers)
            except Exception as e:
                if CONF.message_report_error_allowed:
                    LOG.error(e.message)
                else:
                    raise e


def get_token():
    token_api_endpoint = CONF.openstack_credential.auth_url + '/auth/tokens'
    json_payload = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": CONF.openstack_credential.username,
                        "domain": {
                            "id": CONF.openstack_credential.user_domain_id,
                        },
                        "password": CONF.openstack_credential.password
                    }
                }
            }
        }
    }

    headers = {'content-type': 'application/json',
               'accept': 'application/json'}

    resp = requests.post(token_api_endpoint,
                         data=json.dumps(json_payload),
                         headers=headers)
    return resp.headers.get('X-Subject-Token', None)
