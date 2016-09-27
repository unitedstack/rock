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

from oslo_log import log as logging
import taskflow.engines
from taskflow.patterns import linear_flow
import flow_utils
from taskflow.persistence import models
import contextlib
from taskflow.persistence.backends import impl_sqlalchemy
from oslo_config import cfg
from oslo_utils import importutils

LOG = logging.getLogger(__name__)


CONF = dict(connection=cfg.CONF.database.connection)


def get_tasks_objects(task_cls_name):
    result = []
    for i in task_cls_name:
        result.append(importutils.import_class(i)())
    return result


def get_tasks_cls_name(tasks):
    result = []
    for task in tasks:
        task_name = 'rock.tasks.' + task + '.'
        cls_name = task.split('_')
        for word in cls_name:
            task_name += (word[0].upper() + word[1:])
        result.append(task_name)
    return result


def create_flow(flow_name, tasks):
    task_flow = linear_flow.Flow(flow_name)
    task_cls_name = get_tasks_cls_name(tasks)
    task_flow.add(
        *get_tasks_objects(task_cls_name)
    )

    return task_flow


def run_flow(flow_name, store_spec, tasks):
    """Constructs and run a task flow.
    """

    backend = impl_sqlalchemy.SQLAlchemyBackend(CONF)
   
    book = models.LogBook(flow_name)
    
    with contextlib.closing(backend.get_connection()) as conn:
        conn.save_logbook(book)
    # Now load (but do not run) the flow using the provided initial data.
    flow_engine = taskflow.engines.load_from_factory(create_flow,
                                                     factory_args=(flow_name,
                                                                   tasks),
                                                     store=store_spec,
                                                     backend=backend,
                                                     book=None,
                                                     engine='serial')

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        flow_engine.run()
        LOG.info("taskflow execute is successfully.")
