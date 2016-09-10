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
LOG = logging.getLogger(__name__)


CONF = dict(connection=cfg.CONF.database.connection)


def run_flow(flow_name,store_spec,tasks):
    """Constructs and run a task flow.
    """

    task_flow = linear_flow.Flow(flow_name)

    task_flow.add(
        *tasks
    )

    backend = impl_sqlalchemy.SQLAlchemyBackend(CONF)
    
    book_id = None
    flow_id = None
   
    try:
        book = models.LogBook(flow_name)
        flow_detail = models.FlowDetail("root",uuid=uuidutils.generate_uuid())
        book.add(flow_detail)
        with contextlib.closing(backend.get_connection()) as conn:
            conn.save_logbook(book)
        LOG.info("!! Your tracking id is: '%s+%s'" % (book.uuid,
                                                   flow_detail.uuid))

    except Exception as e:
        LOG.error("task flow is failed.")

    # Now load (but do not run) the flow using the provided initial data.
    flow_engine = taskflow.engines.load_from_factory(task_flow,
                                                    store=store_spec,
                                                    backend=backend,
                                                    book=book,
                                                    engine='serial')

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        flow_engine.run()
        LOG.info("taskflow execute is successfully.")
