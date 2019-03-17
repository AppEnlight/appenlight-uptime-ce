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

import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

import ae_uptime_ce.celery.tasks as tasks

from appenlight.models import DBSession
from appenlight.models.plugin_config import PluginConfig
from appenlight.models.services.application import ApplicationService
from appenlight.models.services.plugin_config import PluginConfigService
from appenlight.views.api import parse_proto
from ae_uptime_ce import PLUGIN_DEFINITION
from ae_uptime_ce.validators import UptimeConfigSchema

log = logging.getLogger(__name__)


@view_config(
    route_name="uptime_api_uptime", renderer="string", permission="uptime_api_access"
)
def uptime_create(request):
    """
    Endpoint for uptime data from probing daemons
    """
    data = request.json_body
    params = dict(request.params.copy())
    proto_version = parse_proto(params.get("protocol_version", ""))
    for entry in data:
        tasks.add_uptime_stats.delay(params, entry)
    msg = "UPTIME call %s client:%s"
    log.info(msg % (proto_version, request.headers.get("user_agent")))
    return "OK: uptime metrics accepted"


@view_config(
    route_name="uptime_api_uptime_app_list",
    require_csrf=False,
    renderer="json",
    permission="uptime_api_access",
)
def get_uptime_app_list(request):
    """
    Returns list of all applications with their uptime urls
    requires create permissions because this is what local security policy returns
    by default
    """
    rows = PluginConfigService.by_query(plugin_name="ae_uptime_ce", section="resource")
    return [{"id": r.resource_id, "url": r.config["uptime_url"]} for r in rows]


@view_config(
    route_name="plugin_configs",
    match_param="plugin_name=" + PLUGIN_DEFINITION["name"],
    renderer="json",
    permission="edit",
    request_method="POST",
)
def post(request):
    schema = UptimeConfigSchema()
    json_body = request.unsafe_json_body
    plugin = PluginConfig()
    plugin.config = {}
    plugin.plugin_name = PLUGIN_DEFINITION["name"]
    plugin.owner_id = request.user.id

    if json_body["section"] == "global":
        # admin config
        plugin.config = json_body["config"]
        plugin.section = "global"
    else:
        # handle user uptime_url
        deserialized = schema.deserialize(json_body["config"])
        plugin.config = deserialized
        plugin.section = "resource"
    if request.context.resource:
        plugin.resource_id = request.context.resource.resource_id
    plugin.config["json_config_version"] = 1
    DBSession.add(plugin)
    DBSession.flush()
    return plugin


@view_config(
    route_name="plugin_config",
    match_param="plugin_name=" + PLUGIN_DEFINITION["name"],
    renderer="json",
    permission="edit",
    request_method="PATCH",
)
def patch(request):
    row = PluginConfigService.by_id(plugin_id=request.matchdict.get("id"))
    if not row:
        raise HTTPNotFound()
    json_body = request.unsafe_json_body
    if json_body["section"] == "global":
        row.config = json_body["config"]
    else:
        schema = UptimeConfigSchema()
        deserialized = schema.deserialize(json_body["config"])
        row.config = deserialized
    return row
