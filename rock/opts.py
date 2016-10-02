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

default_opts = [
    cfg.BoolOpt('message_report_error_allowed',
                default=True,
                help='when failed to report evacuation message,'
                     ' terminate rock-engine or not'),
    cfg.StrOpt('message_report_to',
               default='activemq',
               help="what system should message be reported to. current valid "
                    "value is 'activemq' or 'kiki'"),
    cfg.StrOpt('rock_mon_log_file',
               default='rock-mon.log',
               help='rock monitor log file name'),
    cfg.StrOpt('rock_engine_log_file',
               default='rock-engine.log',
               help='rock engine log file name'),
    cfg.IntOpt('check_cases_interval',
               default=300,
               help="Time interval to check all cases.")
]

host_mgmt_ping_opts = [
    cfg.ListOpt(
        'compute_hosts',
        default=[],
        help="All compute host name. Note the order of following ip addresses"
             " must keep consistent to me"),
    cfg.ListOpt(
        'management_network_ip',
        default=[],
        help="Management ip addresses of compute hosts"),
    cfg.ListOpt(
        'tunnel_network_ip',
        default=[],
        help="Tunnel network ip of compute hosts"),
    cfg.ListOpt(
        'storage_network_ip',
        default=[],
        help="Storage network ip of compute hosts")
]

openstack_credential_opts = [
    cfg.StrOpt('username', default='admin'),
    cfg.StrOpt('user_domain_id', default='default'),
    cfg.StrOpt('nova_client_version', default='2.0'),
    cfg.StrOpt('auth_url', default=None),
    cfg.StrOpt('project_name', default='admin'),
    cfg.StrOpt('project_domain_id', default='default'),
    cfg.StrOpt('password', default=None)
]

host_evacuate_opts = [
    cfg.IntOpt(
        'check_times',
        default=6,
        help="how many times to check the evacuated server's status"),
    cfg.IntOpt(
        'check_interval', default=15, help='check interval')
]

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

kiki_opts = [
    cfg.StrOpt(
        'mail_api_endpoint',
        default='http://10.0.100.41:8200/v1/publish/publish_email'),
    cfg.ListOpt(
        'mail_address',
        default=[])
]


def list_opts():
    """All the options required by rock.

    Because options for oslo_log and oslo_db have been already been registered,
    so we should not register these option again. We should only override these
    options in section [DEFAULT] or [database] in rock.ini.

    :return: list of tuples - [(section, opts_list), ...]
    """
    return [
        (None, default_opts),
        ('host_mgmt_ping', host_mgmt_ping_opts),
        ('openstack_credential', openstack_credential_opts),
        ('host_evacuate', host_evacuate_opts),
        ('activemq', activemq_opts),
        ('kiki', kiki_opts)
    ]
