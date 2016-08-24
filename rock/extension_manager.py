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

import abc
import imp
import os
import six
import eventlet
import Queue

from oslo_log import log as logging
from oslo_config import cfg
from oslo_service import service
from oslo_utils import importutils
from oslo_service import loopingcall


LOG = logging.getLogger(__name__)

@six.add_metaclass(abc.ABCMeta)
class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions."""

    @abc.abstractmethod
    def get_name(self):
        """The name of the extension.

        e.g. 'Fox In Socks'
        """

    @abc.abstractmethod
    def get_alias(self):
        """The alias for the extension.

        e.g. 'FOXNSOX'
        """

    @abc.abstractmethod
    def get_description(self):
        """Friendly description for the extension.

        e.g. 'The Fox In Socks Extension'
        """

    @abc.abstractmethod
    def periodic_task(self):
        """Task that you need to run periodically.

        e.g. 'ping to xxx'
        """


class ExtensionManager(object):
    """Load extensions from the configured extension path.

    See tests/unit/extensions/foxinsocks.py for an
    example extension implementation.
    """

    def __init__(self, path):
        LOG.info('Initializing extension manager.')
        self.path = path
        self.extensions = {}
        self.periodic_tasks = {}
        self._load_all_extensions()

    def _load_all_extensions(self):
        """Load extensions from the configured path.

        The extension name is constructed from the module_name. If your
        extension module is named widgets.py, the extension class within that
        module should be 'Widgets'.

        See tests/unit/extensions/foxinsocks.py for an example extension
        implementation.
        """

        for path in self.path.split(':'):
            if os.path.exists(path):
                self._load_all_extensions_from_path(path)
            else:
                LOG.error("Extension path '%s' doesn't exist!", path)

    def _load_all_extensions_from_path(self, path):
        # Sorting the extension list makes the order in which they
        # are loaded predictable across a cluster of load-balanced
        # Neutron Servers

        for f in sorted(os.listdir(path)):
            try:
                LOG.debug('Loading extension file: %s', f)
                mod_name, file_ext = os.path.splitext(os.path.split(f)[-1])
                ext_path = os.path.join(path, f)
                if file_ext.lower() == '.py' and not mod_name.startswith('_'):
                    mod = imp.load_source(mod_name, ext_path)
                    ext_name = mod_name[0].upper() + mod_name[1:]
                    new_ext_class = getattr(mod, ext_name, None)
                    if not new_ext_class:
                        LOG.warning('Did not find expected name '
                                        '"%(ext_name)s" in %(file)s',
                                    {'ext_name': ext_name,
                                     'file': ext_path})
                        continue
                    new_ext = new_ext_class()
                    self.add_extension(new_ext)
            except Exception as exception:
                LOG.warning("Extension file %(f)s wasn't loaded due to "
                                "%(exception)s",
                            {'f': f, 'exception': exception})

    def add_extension(self, ext):
        alias = ext.get_alias()
        LOG.info('Loaded extension: %s', alias)

        if alias in self.extensions:
            raise exceptions.DuplicatedExtension(alias=alias)
        self.extensions[alias] = ext

    def _report_state(self):
        print("State report, existing loading extensions: "
            + str(self.extensions))

    def report_state_loop(self):
        eventlet.spawn(self._report_state)


    def after_start(self):
        for ext in self.extensions:
            task = getattr(self.extensions[ext], 'periodic_task')
            self.periodic_tasks[ext] = loopingcall.FixedIntervalLoopingCall(task)
            self.periodic_tasks[ext].start(interval=10)
