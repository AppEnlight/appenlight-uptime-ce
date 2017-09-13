# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pkg_resources

__license__ = 'Apache 2.0'
__author__ = 'RhodeCode GmbH'
__url__ = 'http://rhodecode.com'

PLUGIN_DEFINITION = {
    'name': 'ae_uptime_ce',
    'config': {'celery_tasks': ['ae_uptime_ce.celery.tasks'],
               'fulltext_indexer': 'ae_uptime_ce.scripts.reindex:reindex_uptime',
               'sqlalchemy_migrations': 'ae_uptime_ce:migrations',
               'default_values_setter': 'ae_uptime_ce.scripts:set_default_values',
               'javascript': {
                   'src': 'ae_uptime_ce.js',
                   'angular_module': 'appenlight.plugins.ae_uptime_ce'
               },
               'static': pkg_resources.resource_filename('ae_uptime_ce',
                                                         'static')
               }
}


def includeme(config):
    """Add the application's view handlers.
    """
    config.add_route('uptime_api_uptime', '/api/uptime')
    config.add_route('uptime_api_uptime_app_list', '/api/uptime_app_list')
    config.register_appenlight_plugin(
        PLUGIN_DEFINITION['name'],
        PLUGIN_DEFINITION['config']
    )
    config.scan('ae_uptime_ce',
                ignore=['ae_uptime_ce.scripts'])
