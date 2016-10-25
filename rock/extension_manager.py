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
import threading
import time

import six
from oslo_log import log as logging
from rock import exceptions

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions."""

    @abc.abstractmethod
    def get_name(self):
        """The name of the extension.

        e.g. 'Host Management IP Ping'
        """

    @abc.abstractmethod
    def get_alias(self):
        """The alias for the extension.

        e.g. 'host-mgmt-ping'
        """

    @abc.abstractmethod
    def get_description(self):
        """Friendly description for the extension.

        e.g. 'Delay of ping to management IP of host.'
        """

    @abc.abstractmethod
    def periodic_task(self):
        """Task that you need to run periodically.

        e.g. 'ping to xxx'
        """

    @staticmethod
    def period_decorator(interval=10):
        def wrapper(func):
            def _wrapper(*args, **kwargs):
                result = None
                while True:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    used_time = round(end_time - start_time, 3)
                    if interval - used_time < 0:
                        LOG.warning("Plugin: %s run outlasted interval by"
                                    " %.3f seconds." % (func.__module__,
                                                        used_time - interval))
                        time.sleep(0)
                    else:
                        time.sleep(interval - used_time)
                return result

            return _wrapper

        return wrapper


class ExtensionManager(object):
    """Load extensions from the configured extension path.

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
        """

        for path in self.path.split(':'):
            if os.path.exists(path):
                self._load_all_extensions_from_path(path)
            else:
                LOG.error("Extension path '%s' doesn't exist!", path)

    def _load_all_extensions_from_path(self, path):

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
                            "%(exception)s", {'f': f,
                                              'exception': exception})

    def add_extension(self, ext):
        alias = ext.get_alias()
        LOG.info('Loaded extension: %s', alias)

        if alias in self.extensions:
            raise exceptions.DuplicatedExtension(alias=alias)
        self.extensions[alias] = ext

    @ExtensionDescriptor.period_decorator(60)
    def report_status(self):
        current_thread_list = threading.enumerate()
        thread_name = []
        for thread in current_thread_list:
            if thread.name in self.extensions:
                thread_name.append(thread.name)
        LOG.info("Current plugin threads: %s" % thread_name)

        # If some extensions threads exit unexpectedly, create a new thread
        # for it
        none_thread_extensions = [i for i in self.extensions
                                  if i not in thread_name]
        if len(none_thread_extensions) > 0:
            LOG.info("Recreate threads for extension(s): %s"
                     % none_thread_extensions)
            for ext in none_thread_extensions:
                task = getattr(self.extensions[ext], 'periodic_task')
                task_name = ext
                t = threading.Thread(target=task, name=task_name)
                t.start()

    def start_collect_data(self):
        for extension in self.extensions:
            task = getattr(self.extensions[extension], 'periodic_task')
            task_name = extension
            t = threading.Thread(target=task, name=task_name)
            t.start()
        t = threading.Thread(
            target=self.report_status, name='Plugins-Status-Report')
        t.start()
