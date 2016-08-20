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

"""API for database access.
"""

from oslo_config import cfg
from oslo_db import api as db_api
from oslo_utils import timeutils


_BACKEND_MAPPING = {'sqlalchemy': 'rock.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


def get_last_n_records(model, n, sort_key=None):
    return IMPL.get_last_n_records(model, n, sort_key=sort_key)


def get_period_records(model, start_time, end_time=timeutils.utcnow(),
        sort_key='id', sort_dir='asc'):
    return IMPL.get_period_records(model, start_time, end_time=end_time,
            sort_key=sort_key, sort_dir=sort_dir)


def save(model_obj):
    IMPL.save(model_obj)


def save_all(model_objs):
    IMPL.save_all(model_objs)

