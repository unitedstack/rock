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

"""SQLAlchemy base model for rock
"""

from oslo_db.sqlalchemy import models
from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from oslo_utils import timeutils


class ModelBase(models.ModelBase):

    id = Column(Integer(), primary_key=True)
    create_at = Column(DateTime(), default=lambda: timeutils.utcnow())
    target = Column(String(36))
    result = Column(Boolean(), default=False)

    def save(self, session=None):
        import rock.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(ModelBase, self).save(session)
