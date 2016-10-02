# -*- coding: utf-8 -*-

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

import pbr.version
from rock.db import api as db_api

__version__ = pbr.version.VersionInfo(
    'rock').version_string()

# Initialize rock database backend, because some module in rock implemented db
# backend themselves, not use rock.db module. But need a database connection
# configuration. So, as a temporary solution, we initialize rock db
# backend here to make some option registered in oslo_config.cfg.CONF.
