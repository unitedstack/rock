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
from oslo_db.sqlalchemy import session as db_session
from oslo_utils import timeutils
from sqlalchemy import desc

from rock.db.sqlalchemy.model_base import ModelBase

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


class Connection(object):
    """SQLAlchemy connection"""

    def __init__(self):
        pass

    def get_last_n_records(self, model, n, sort_key='id', sort_dir='desc'):
        query = model_query(model)
        query = query.order_by(desc(model.id))
        query = query.limit(n)
        if sort_dir == 'desc':
            try:
                result = query.all()
                return result
            except Exception:
                raise
        else:
            try:
                result = query.from_self().\
                         order_by(getattr(model, sort_key)).all()
                return result
            except Exception:
                raise

    def get_period_records(self,
                           model,
                           start_time,
                           end_time=timeutils.utcnow(),
                           sort_key='id',
                           sort_dir='desc'):
        query = model_query(model)
        query = query.filter(model.create_at >= start_time,
                             model.create_at <= end_time)
        if sort_dir == 'desc':
            try:
                result = query.from_self().\
                         order_by(desc(getattr(model, sort_key))).all()
                return result
            except Exception:
                raise
        else:
            try:
                result = query.from_self().\
                         order_by(getattr(model, sort_key)).all()
                return result
            except Exception:
                raise

    def save(self, model_obj, session=get_session()):
        try:
            model_obj.save()
        except Exception:
            raise

    @staticmethod
    def save_all(model_objs, session=get_session()):
        try:
            ModelBase.save_all(model_objs, session=session)
        except Exception:
            raise

