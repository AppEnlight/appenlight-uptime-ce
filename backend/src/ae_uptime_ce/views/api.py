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


@view_config(route_name='uptime_api_uptime', renderer='string',
             permission='uptime_api_access')
def uptime_create(request):
    """
    Endpoint for uptime data from probing daemons
    """
    data = request.json_body
    application = ApplicationService.by_id(data.get('resource'))
    if not application:
        raise HTTPNotFound()
    params = dict(request.params.copy())
    proto_version = parse_proto(params.get('protocol_version', ''))
    tasks.add_uptime_stats.delay(application.resource_id, params, data)
    msg = 'UPTIME call %s %s client:%s'
    log.info(msg % (application, proto_version,
                    request.headers.get('user_agent')))
    return 'OK: uptime metrics accepted'


@view_config(route_name='uptime_api_uptime_app_list', require_csrf=False,
             renderer='json', permission='uptime_api_access')
def get_uptime_app_list(request):
    """
    Returns list of all applications with their uptime urls
    requires create permissions because this is what local security policy returns
    by default
    """
    rows = PluginConfigService.by_query(plugin_name='ae_uptime_ce',
                                 section='resource')
    return [{'id': r.resource_id, 'url': r.config['uptime_url']} for r in rows]


@view_config(route_name='plugin_configs',
             match_param='plugin_name=' + PLUGIN_DEFINITION['name'],
             renderer='json', permission='edit', request_method='POST')
def post(request):
    schema = UptimeConfigSchema()
    json_body = request.unsafe_json_body
    plugin = PluginConfig()
    plugin.config = {}
    plugin.plugin_name = PLUGIN_DEFINITION['name']
    plugin.owner_id = request.user.id

    if json_body['section'] == 'global':
        # admin config
        plugin.config = json_body['config']
        plugin.section = 'global'
    else:
        # handle user uptime_url
        deserialized = schema.deserialize(json_body['config'])
        plugin.config = deserialized
        plugin.section = 'resource'
    if request.context.resource:
        plugin.resource_id = request.context.resource.resource_id
    plugin.config['json_config_version'] = 1
    DBSession.add(plugin)
    DBSession.flush()
    return plugin


@view_config(route_name='plugin_config',
             match_param='plugin_name=' + PLUGIN_DEFINITION['name'],
             renderer='json', permission='edit', request_method='PATCH')
def patch(request):
    row = PluginConfigService.by_id(plugin_id=request.matchdict.get('id'))
    if not row:
        raise HTTPNotFound()
    json_body = request.unsafe_json_body
    if json_body['section'] == 'global':
        row.config = json_body['config']
    else:
        schema = UptimeConfigSchema()
        deserialized = schema.deserialize(json_body['config'])
        row.config = deserialized
    return row
