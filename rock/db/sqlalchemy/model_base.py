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
    created_at = Column(DateTime(),
                        default=lambda: timeutils.utcnow(),
                        nullable=False)
    target = Column(String(36), nullable=False)
    result = Column(Boolean(), nullable=False)

    def save(self, session=None):
        super(ModelBase, self).save(session)

    @staticmethod
    def save_all(model_objs, session=None):
        with session.begin(subtransactions=True):
            session.add_all(instances=model_objs)
            session.flush()
