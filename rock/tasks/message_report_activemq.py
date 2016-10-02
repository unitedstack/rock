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

import time

import stomp
from oslo_config import cfg
from oslo_log import log as logging

from flow_utils import BaseTask

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

activemq_group = cfg.OptGroup('activemq')
activemq_opts = [
    cfg.StrOpt(
        'username',
        default=None,
        help='the username to connect with'),
    cfg.StrOpt(
        'password',
        default=None,
        help='the password used to authenticate with'),
    cfg.StrOpt(
        'server_ip',
        default='127.0.0.1',
        help='the ipaddress of activemq server'),
    cfg.IntOpt(
        'server_port',
        default=61613,
        help='the port of of activemq server'),
    cfg.StrOpt(
        'destination',
        default='eventQueue',
        help='the queue or topic name of activemq '
             'where the message reported to')
]

message_report_error_allowed_opt = \
    cfg.BoolOpt('message_report_error_allowed',
                default=True,
                help='when failed to report evacuation message,'
                     ' terminate rock-engine or not.')

CONF.register_opt(message_report_error_allowed_opt)
CONF.register_group(activemq_group)
CONF.register_opts(activemq_opts, activemq_group)


class ConnectionListener(stomp.ConnectionListener):
    def on_error(self, headers, body):
        LOG.error("Can't send message to queue due to: \n%s" % body)

    def on_send(self, frame):
        LOG.info("Sending message: %s to activemq server." % frame)

    def on_connecting(self, host_and_port):
        LOG.info("Connecting to activemq server: %s" % str(host_and_port))

    def on_connected(self, headers, body):
        LOG.info("Successfully connected to activemq server.")

    def on_disconnected(self):
        LOG.info("Disconnect to activemq server.")


class MessageReport(BaseTask):
    def execute(self, message_body, message_destination=None,
                message_content_type=None, message_headers=None,
                message_keyword_headers=None):

        if message_headers is None:
            message_headers = {}
        if message_keyword_headers is None:
            message_keyword_headers = {}
        host_and_port = [(CONF.activemq.server_ip, CONF.activemq.server_port)]
        if message_destination is None:
            message_destination = '/queue/' + CONF.activemq.destination
        connection = stomp.Connection(host_and_port)
        connection.set_listener(
            'activemq_connection_listener', ConnectionListener())
        try:
            connection.start()
            connection.connect(
                username=CONF.activemq.username,
                passcode=CONF.activemq.password, wait=True)
            for message in message_body:
                connection.send(
                    destination=message_destination,
                    body=message,
                    content_type=message_content_type,
                    headers=message_headers,
                    keyword_headers=message_keyword_headers)
            time.sleep(1)
            connection.disconnect()
        except Exception as err:
            if CONF.message_report_error_allowed:
                LOG.error("Activemq error: %s" % err.message)
            else:
                raise err
