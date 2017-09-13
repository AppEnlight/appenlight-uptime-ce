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

from datetime import datetime, timedelta
from pyramid.view import view_config

from ae_uptime_ce import PLUGIN_DEFINITION
from appenlight.lib.utils import build_filter_settings_from_query_dict
from appenlight.models.services.plugin_config import PluginConfigService
from appenlight.validators import PermissiveDate
from ae_uptime_ce.models.services.uptime_metric import \
    UptimeMetricService

log = logging.getLogger(__name__)


@view_config(route_name='applications_property', match_param='key=uptime',
             renderer='json', permission='view')
def uptime(request):
    """
    Returns uptime information: current uptime, daily and monthly stats
    """
    application = request.context.resource
    now = datetime.utcnow().replace(microsecond=0, second=0)
    location_dict = {}

    row = PluginConfigService.by_query(
        section='global', plugin_name=PLUGIN_DEFINITION['name']).first()

    if row:
        for x, location in enumerate(row.config['uptime_regions_map'], 1):
            location_dict[x] = {'country': location['country'].lower(),
                                'city': location['name']}

    if request.GET.get('start_date'):
        delta = now - PermissiveDate().deserialize(
            None, request.GET.get('start_date'))
    else:
        delta = timedelta(hours=1)
    stats_since = now - delta
    uptime = UptimeMetricService.get_uptime_by_app(
        application.resource_id, stats_since, until=now)
    latest_stats = UptimeMetricService.get_uptime_stats(
        application.resource_id).all()
    daily_stats = UptimeMetricService.get_daily_uptime_stats(
        application.resource_id).all()
    daily_list = []
    monthly_list = []
    for i, stat_list in enumerate([daily_stats, latest_stats]):
        for j, entry in enumerate(stat_list):

            item = {
                'id': j,
                'total_checks': getattr(entry, 'total_checks', 0),
                'retries': entry.tries,
                'avg_response_time': entry.response_time or 0,
                'status_code': entry.status_code,
                'location': location_dict.get(getattr(entry, 'location', None),
                                              {'city': 'unknown',
                                               'country': 'us'})
            }
            if i == 1:
                item['interval'] = entry.interval.strftime('%Y-%m-%dT%H:%M')
                item['timestamp'] = entry.interval
                daily_list.append(item)
            else:
                item['interval'] = entry.interval.strftime('%Y-%m-%d')
                monthly_list.append(item)

    return {'current_uptime': uptime,
            "latest_stats": daily_list,
            "monthly_stats": monthly_list}


@view_config(route_name='applications_property', renderer='json',
             match_param='key=uptime_graphs', permission='view')
def uptime_graphs(request):
    """
    Returns uptime information: current uptime, daily and monthly stats
    """
    query_params = request.GET.mixed().copy()
    query_params['resource'] = (request.context.resource.resource_id,)
    filter_settings = build_filter_settings_from_query_dict(request,
                                                            query_params)

    if not filter_settings.get('end_date'):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings['end_date'] = end_date

    if not filter_settings.get('start_date'):
        delta = timedelta(hours=1)
        filter_settings['start_date'] = filter_settings['end_date'] - delta

    plot_data = UptimeMetricService.uptime_for_resource(
        request, filter_settings)

    return plot_data
