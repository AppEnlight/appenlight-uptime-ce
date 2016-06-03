# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# App Enlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

import pkg_resources

PLUGIN_DEFINITION = {
    'name': 'ae_uptime_ce',
    'config': {'celery_tasks': ['ae_uptime_ce.celery.tasks'],
               'fulltext_indexer': 'ae_uptime_ce.scripts.reindex:reindex_uptime',
               'sqlalchemy_migrations': 'ae_uptime_ce:migrations',
               'default_values_setter': 'ae_uptime_ce.scripts:set_default_values',
               'top_nav': {
                   'menu_dashboards_items': {'sref': 'uptime',
                                             'label': 'Uptime Statistics'}
               },
               'javascript': {
                   'src': 'ae_uptime_ce.js',
                   'angular_module': 'appenlight.plugins.ae_uptime_ce'
               },
               'static': pkg_resources.resource_filename('ae_uptime_ce', 'static')
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
