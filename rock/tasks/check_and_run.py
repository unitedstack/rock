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
import flow_utils
import contextlib
from taskflow.persistence.backends import impl_sqlalchemy
from oslo_config import cfg
from taskflow import exceptions as exc
import sql_exec

LOG = logging.getLogger(__name__)

CONF = dict(connection=cfg.CONF.database.connection)


def check_and_run():
    backend = impl_sqlalchemy.SQLAlchemyBackend(CONF)
    if sql_exec.flowdetails is None:
        return

    if sql_exec.flowdetails[5] != u'SUCCESS':
        book_id = sql_exec.flowdetails[2]
        flow_id = sql_exec.flowdetails[6]

    else:
        return

    flow_detail = None

    if all([book_id, flow_id]):
        try:
            with contextlib.closing(backend.get_connection()) as conn:
                lb = conn.get_logbook(book_id)
                flow_detail = lb.find(flow_id)

        except exc.NotFound:
            pass

    flow_engine = taskflow.engines.load_from_detail(flow_detail,
                                                    backend=backend,
                                                    engine='serial')

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        LOG.info("Starting to run previously unfinished task flow")
        flow_engine.run()
        LOG.info("The previously partially completed flow is finished.")
