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

import requests
import stomp
from oslo_config import cfg
from oslo_log import log as logging

from flow_utils import BaseTask

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class ConnectionListener(stomp.ConnectionListener):
    def on_error(self, headers, body):
        LOG.error("Can't send message to queue due to: %s" % body)

    def on_send(self, frame):
        LOG.info("Sending message: %s" % frame)

    def on_connecting(self, host_and_port):
        LOG.info("Connecting to activemq server: %s" % str(host_and_port))

    def on_connected(self, headers, body):
        LOG.info("Successfully connected to activemq server.")

    def on_disconnected(self):
        LOG.info("Disconnect to activemq server.")


class MessageReport(BaseTask):
    def execute(self, message_body, message_content_type=None,
                message_headers=None):
        if CONF.message_report_to == 'activemq':
            reporter = Activemq(body=message_body,
                                content_type=message_content_type,
                                headers=message_headers)
            reporter.report_message()
        elif CONF.message_report_to == 'kiki':
            reporter = Kiki(body=message_body, mail_subject=None)
            reporter.report_message()
        else:
            LOG.error(
                " messaging system: %s is not supported" %
                CONF.message_report_to)


class Activemq(object):
    def __init__(self, body, content_type=None, headers=None):
        self.body = body
        self.content_type = content_type
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        self.host_and_port = [
            (CONF.activemq.server_ip, CONF.activemq.server_port)]
        self.destination = '/queue/' + CONF.activemq.destination

    def report_message(self):
        connection = stomp.Connection(self.host_and_port)
        connection.set_listener(
            'activemq_connection_listener', ConnectionListener())
        try:
            connection.start()
            connection.connect(
                username=CONF.activemq.username,
                passcode=CONF.activemq.password, wait=True)
            for body in self.body:
                connection.send(
                    destination=self.destination,
                    body=body,
                    content_type=self.content_type,
                    headers=self.headers)
            connection.disconnect()
        except Exception as err:
            if CONF.message_report_error_allowed:
                LOG.error("Activemq error: %s" % err.message)
            else:
                raise err


class Kiki(object):
    def __init__(self, body, mail_subject=None):
        self.body = body
        self.mail_api_endpoint = CONF.kiki.mail_api_endpoint
        self.token_api_endpoint = \
            CONF.openstack_credential.auth_url + '/auth/tokens'
        self.mail_address = CONF.kiki.mail_address
        if mail_subject is None:
            self.mail_subject = 'Compute host HA operation'
        else:
            self.mail_subject = mail_subject
        self.mail_content = json.dumps(self.body)
        self.http_headers = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.get_token()
        }

    def report_message(self):
        LOG.info("Starting send mail use kiki api to %s" % self.mail_address)
        LOG.info("Content: %s" % self.mail_content)
        for address in self.mail_address:
            data = {
                "to": address,
                "subject": self.mail_subject,
                "content": self.mail_content
            }
            try:
                requests.post(self.mail_api_endpoint,
                              data=json.dumps(data),
                              headers=self.http_headers)
            except Exception as e:
                if CONF.message_report_error_allowed:
                    LOG.error(e.message)
                else:
                    raise e

    def get_token(self):
        json_payload = {
            "auth": {
                "identity": {
                    "methods": ["password"],
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

        resp = requests.post(self.token_api_endpoint,
                             data=json.dumps(json_payload),
                             headers=headers)
        return resp.headers.get('X-Subject-Token', None)
