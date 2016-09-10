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

import sys
from oslo_log import log as logging
import taskflow.engines
from taskflow.patterns import linear_flow
import flow_utils
from taskflow.persistence import models 
from oslo_utils import uuidutils
import contextlib
from taskflow.persistence.backends import impl_sqlalchemy
from oslo_config import cfg
import sql_exec
from oslo_utils import importutils

LOG = logging.getLogger(__name__)


CONF = dict(connection=cfg.CONF.database.connection)

def get_tasks_cls_name(tasks):
    result = []
    for task in tasks:
        task_module_str = task.__module__
        module_name = task_module_str.split('.')[-1]
        cls_name = ''
        for i in module_name.split('_'):
            cls_name += (i[0].upper() + i[1:])
        result.append(task_module_str + '.' + cls_name)
    return result

def get_tasks_objects(task_cls_name):
    result = []
    for i in task_cls_name:
        result.append(importutils.import_class(i)())
    return result

def create_flow(flow_name, tasks_cls_name):
    task_flow = linear_flow.Flow(flow_name)
    tasks = get_tasks_objects(tasks_cls_name)
    task_flow.add(
        *tasks
    )

    return task_flow

def run_flow(flow_name,store_spec,tasks):
    """Constructs and run a task flow.
    """

    backend = impl_sqlalchemy.SQLAlchemyBackend(CONF)
    book_id = None
    flow_id = None
   
    #book = models.LogBook(flow_name)
    
    #with contextlib.closing(backend.get_connection()) as conn:
    #    conn.save_logbook(book)
    tasks_cls_name = get_tasks_cls_name(tasks)
    # Now load (but do not run) the flow using the provided initial data.
    flow_engine = taskflow.engines.load_from_factory(create_flow,
                                                    factory_args=(flow_name, tasks_cls_name),
                                                    store=store_spec,
                                                    backend=backend,
                                                    book=None,
                                                    engine='serial')

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        flow_engine.run()
        LOG.info("taskflow execute is successfully.")
