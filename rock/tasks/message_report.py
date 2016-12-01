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
