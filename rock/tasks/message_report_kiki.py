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

kiki_opt_group = cfg.OptGroup('kiki')
kiki_opts = [
    cfg.StrOpt(
        'mail_api_endpoint',
        default='http://10.0.100.41:8200/v1/publish/publish_email'),
    cfg.ListOpt(
        'mail_address',
        default=['hebin@unitedstack.com'])
]
CONF = cfg.CONF
CONF.register_group(kiki_opt_group)
CONF.register_opts(kiki_opts, kiki_opt_group)

if getattr(CONF, 'message_report_error_allowed') is None:
    CONF.register_opt(
        cfg.BoolOpt('message_report_error_allowed = true', default=True))


class MessageReportKiki(BaseTask):
    def execute(self, message_body):
        mail_api_endpoint = CONF.kiki.mail_api_endpoint
        mail_address = CONF.kiki.mail_address
        mail_content = json.dumps(message_body)
        mail_subject = 'Compute host HA operation'
        http_headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': '8f7374d8e10c4a6eb3d24b23a9e8a68a'
        }

        for address in mail_address:
            data = {
                "to": address,
                "subject": mail_subject,
                "content": mail_content
            }
            try:
                requests.post(mail_api_endpoint,
                              json=data,
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
                        "password": "dffcb42eb3a0c8795cbea277"
                    }
                }
            }
        }
    }
