# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.

from falcon import testing as ftest
from oslo.config import cfg

import marconi.queues
from marconi.queues.transport.wsgi import driver
from marconi import tests as testing
from marconi.tests import faulty_storage


class TestBase(testing.TestBase):

    config_filename = None

    def setUp(self):
        if self.config_filename is None:
            self.skipTest('No config specified')

        super(TestBase, self).setUp()

        conf = cfg.ConfigOpts()
        conf(default_config_files=[self.conf_path(self.config_filename)])
        conf.register_opts(driver._WSGI_OPTIONS,
                           group=driver._WSGI_GROUP)
        self.wsgi_cfg = conf[driver._WSGI_GROUP]

        self.boot = marconi.Bootstrap(conf)

        self.app = self.boot.transport.app
        self.srmock = ftest.StartResponseMock()

    def simulate_request(self, path, project_id=None, **kwargs):
        """Simulate a request.

        Simulates a WSGI request to the API for testing.

        :param path: Request path for the desired resource
        :param project_id: Project ID to use for the X-Project-ID header,
            or None to not set the header
        :param kwargs: Same as falcon.testing.create_environ()

        :returns: standard WSGI iterable response
        """

        if project_id is not None:
            headers = dict(kwargs['headers']) if 'headers' in kwargs else {}
            headers['X-Project-ID'] = project_id
            kwargs['headers'] = headers

        return self.app(ftest.create_environ(path=path, **kwargs),
                        self.srmock)

    def simulate_get(self, *args, **kwargs):
        """Simulate a GET request."""
        kwargs['method'] = 'GET'
        return self.simulate_request(*args, **kwargs)

    def simulate_head(self, *args, **kwargs):
        """Simulate a HEAD request."""
        kwargs['method'] = 'HEAD'
        return self.simulate_request(*args, **kwargs)

    def simulate_put(self, *args, **kwargs):
        """Simulate a PUT request."""
        kwargs['method'] = 'PUT'
        return self.simulate_request(*args, **kwargs)

    def simulate_post(self, *args, **kwargs):
        """Simulate a POST request."""
        kwargs['method'] = 'POST'
        return self.simulate_request(*args, **kwargs)

    def simulate_delete(self, *args, **kwargs):
        """Simulate a DELETE request."""
        kwargs['method'] = 'DELETE'
        return self.simulate_request(*args, **kwargs)

    def simulate_patch(self, *args, **kwargs):
        """Simulate a PATCH request."""
        kwargs['method'] = 'PATCH'
        return self.simulate_request(*args, **kwargs)


class TestBaseFaulty(TestBase):
    """This test ensures we aren't letting any exceptions go unhandled."""

    def setUp(self):
        self._storage_backup = marconi.Bootstrap.storage
        faulty = faulty_storage.Driver(cfg.ConfigOpts())
        setattr(marconi.Bootstrap, 'storage', faulty)
        super(TestBaseFaulty, self).setUp()

    def tearDown(self):
        setattr(marconi.Bootstrap, 'storage', self._storage_backup)
        super(TestBaseFaulty, self).tearDown()
