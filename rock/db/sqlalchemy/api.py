# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""SQLAlchemy storage backend.
"""

from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_utils import timeutils



CONF = cfg.CONF

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None):
    if not query:
        query = model_query(model)
    sort_keys = ['id']
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise db_exc.InvalidSortKey(sort_key)
    return query.all()


class Connection(object):
    """SQLAlchemy connection"""

    def __init__(self):
        pass

    def get_last_n_records(self, model, n, sort_key='id'):
        query = model_query(model)
        limit = n
        marker = None
        sort_dir = 'desc'
        return _paginate_query(model, limit, marker,
                                sort_key, sort_dir, query)

    def get_period_records(self,
                           model,
                           start_time,
                           end_time=timeutils.utcnow(),
                           sort_key='id',
                           sort_dir='asc'):
        query = model_query(model)
        query = query.filter(model.create_at >= start_time,
                             model.create_at <= end_time)
        result = _paginate_query(model, sort_key=sort_key,
                                sort_dir=sort_dir,query=query)
        return result

    def save(self, model_obj):
        try:
            model_obj.save()
        except Exception:
            raise

    def save_all(self, model_objs):
        for obj in model_objs:
            try:
                obj.save()
            except Exception:
                raise

