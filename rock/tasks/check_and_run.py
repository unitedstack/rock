from oslo_log import log as logging
import taskflow.engines
import flow_utils
from taskflow.engines.helpers import load_from_detail
import contextlib
from taskflow.persistence.backends import impl_sqlalchemy
from oslo_config import cfg
import sql_exec
LOG = logging.getLogger(__name__)


CONF = dict(connection=cfg.CONF.database.connection)

def find_flow_detail(backend, book_id, flow_id):
    # NOTE(harlowja): this is used to attempt to find a given logbook with
    # a given id and a given flow details inside that logbook, we need this
    # reference so that we can resume the correct flow (as a logbook tracks
    # flows and a flow detail tracks a individual flow).
    #   
    # Without a reference to the logbook and the flow details in that logbook
    # we will not know exactly what we should resume and that would mean we
    # can't resume what we don't know.
    with contextlib.closing(backend.get_connection()) as conn:
        lb = conn.get_logbook(book_id)
        return lb.find(flow_id)


def check_and_run():
    backend = impl_sqlalchemy.SQLAlchemyBackend(CONF)
    if sql_exec.flowdetails[5] != 'SUCCESS':
        book_id = sql_exec.flowdetails[2]
        flow_id = sql_exec.flowdetails[6]

    if all([book_id,flow_id]):
        flow_detail = find_flow_detail(backend, book_id, flow_id)
    flow_engine = taskflow.engines.load_from_detail(flow_detail,
                                                    backend=backend,
                                                    engine='serial')

    with flow_utils.DynamicLogListener(flow_engine, logger=LOG):
        flow_engine.run()
        LOG.info("The previously partially completed flow is finished.")

