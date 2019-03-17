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

from ae_uptime_ce import PLUGIN_DEFINITION
from appenlight.models.plugin_config import PluginConfig
from appenlight.models.services.plugin_config import PluginConfigService
from appenlight.models import DBSession


def set_default_values():
    row = PluginConfigService.by_query(
        plugin_name=PLUGIN_DEFINITION["name"], section="global"
    ).first()

    if not row:
        plugin = PluginConfig()
        plugin.config = {"uptime_regions_map": [], "json_config_version": 1}
        plugin.section = "global"
        plugin.plugin_name = PLUGIN_DEFINITION["name"]
        plugin.config["json_config_version"] = 1
        DBSession.add(plugin)
        DBSession.flush()
