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
        flow_engine.run()
        LOG.info("The previously partially completed flow is finished.")
