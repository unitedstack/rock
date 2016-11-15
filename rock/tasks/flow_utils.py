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

import os

from oslo_log import log as logging
from oslo_config import cfg
from keystoneauth1 import identity, session
from novaclient import client
from taskflow.listeners import base
from taskflow.listeners import logging as logging_listener
from taskflow import task

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def _make_task_name(cls, addons=None):
    """Makes a pretty name for a task class."""
    base_name = ".".join([cls.__module__, cls.__name__])
    extra = ''
    if addons:
        extra = ';%s' % (", ".join([str(a) for a in addons]))

    return base_name + extra


class BaseTask(task.Task):
    """The root task class for all tasks.

    It automatically names the given task using the module and class that
    implement the given task as the task name.
    """

    def __init__(self, addons=None, **kwargs):
        super(BaseTask, self).__init__(self.make_name(addons), **kwargs)

    @classmethod
    def make_name(cls, addons=None):
        return _make_task_name(cls, addons)


class DynamicLogListener(logging_listener.DynamicLoggingListener):
    """This is used to attach to taskflow engines while they are running.

    It provides a bunch of useful features that expose the actions happening
    inside a taskflow engine, which can be useful for developers for debugging,
    for operations folks for monitoring and tracking of the resource actions
    and more...
    """

    #: Exception is an excepted case, don't include traceback in log if fails.
    _NO_TRACE_EXCEPTIONS = ()

    def __init__(self, engine,
                 task_listen_for=base.DEFAULT_LISTEN_FOR,
                 flow_listen_for=base.DEFAULT_LISTEN_FOR,
                 retry_listen_for=base.DEFAULT_LISTEN_FOR,
                 logger=LOG):
        super(DynamicLogListener, self).__init__(
            engine,
            task_listen_for=task_listen_for,
            flow_listen_for=flow_listen_for,
            retry_listen_for=retry_listen_for,
            log=logger)

    def _format_failure(self, fail):
        if fail.check(*self._NO_TRACE_EXCEPTIONS) is not None:
            exc_info = None
            exc_details = '%s%s' % (os.linesep, fail.pformat(traceback=False))
            return (exc_info, exc_details)
        else:
            return super(DynamicLogListener, self)._format_failure(fail)


def get_nova_client():
    auth = identity.Password(
        username=CONF.openstack_credential.username,
        password=CONF.openstack_credential.password,
        project_name=CONF.openstack_credential.project_name,
        auth_url=CONF.openstack_credential.auth_url,
        project_domain_id=CONF.openstack_credential.project_domain_id,
        user_domain_id=CONF.openstack_credential.user_domain_id)

    sess = session.Session(auth=auth, verify=False)
    nova_client_version = CONF.openstack_credential.nova_client_version
    n_client = client.Client(nova_client_version, session=sess)
    return n_client
