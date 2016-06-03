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

from ae_uptime_ce import PLUGIN_DEFINITION
from appenlight.models.plugin_config import PluginConfig
from appenlight.models.services.plugin_config import PluginConfigService
from appenlight.models import DBSession


def set_default_values():
    row = PluginConfigService.by_query(plugin_name=PLUGIN_DEFINITION['name'],
                                       section='global').first()

    if not row:
        plugin = PluginConfig()
        plugin.config = {"uptime_regions_map": [], "json_config_version": 1}
        plugin.section = 'global'
        plugin.plugin_name = PLUGIN_DEFINITION['name']
        plugin.config['json_config_version'] = 1
        DBSession.add(plugin)
        DBSession.flush()
