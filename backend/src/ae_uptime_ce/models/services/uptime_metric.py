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
import sqlalchemy as sa
from datetime import datetime, timedelta

import appenlight.lib.helpers as h
from pyramid.threadlocal import get_current_request
from appenlight.lib.utils import es_index_name_limiter
from appenlight.models import get_db_session
from appenlight.models.event import Event
from appenlight.models.services.base import BaseService
from appenlight.models.services.event import EventService
from ae_uptime_ce.models.uptime_metric import UptimeMetric

log = logging.getLogger(__name__)


class UptimeMetricService(BaseService):
    @classmethod
    def get_uptime_by_app(cls, resource_id, since_when, db_session=None,
                          until=None):
        db_session = get_db_session(db_session)
        if not until:
            until = datetime.utcnow()
        query = db_session.query(sa.func.count(UptimeMetric.resource_id))
        query = query.filter(UptimeMetric.start_interval >= since_when)
        query = query.filter(UptimeMetric.start_interval < until)
        query = query.filter(UptimeMetric.resource_id == resource_id)
        query = query.filter(sa.or_(UptimeMetric.response_time == 0,
                                    UptimeMetric.status_code >= 400))

        delta = until - since_when
        minutes = divmod(delta.total_seconds(), 60)[0]
        count = query.scalar()
        if count:
            return round((minutes - float(count)) / minutes * 100, 2)
        return 100

    @classmethod
    def get_uptime_stats(cls, resource_id, db_session=None):
        db_session = get_db_session(db_session)
        now = datetime.utcnow().replace(microsecond=0, second=0)
        floor_func = UptimeMetric.start_interval
        since_when = now - timedelta(hours=1)
        query = db_session.query(floor_func.label('interval'),
                                 UptimeMetric.response_time,
                                 UptimeMetric.tries,
                                 UptimeMetric.status_code,
                                 UptimeMetric.location
                                 )
        query = query.filter(UptimeMetric.resource_id == resource_id)
        query = query.filter(UptimeMetric.start_interval >= since_when)
        query = query.order_by(sa.desc(floor_func))
        return query

    @classmethod
    def get_daily_uptime_stats(cls, resource_id, db_session=None):
        db_session = get_db_session(db_session)
        now = datetime.utcnow().replace(microsecond=0, second=0)
        floor_func = sa.func.date_trunc('day', UptimeMetric.start_interval)
        since_when = now.replace(day=1, minute=0, second=0)
        rt_avg = sa.func.avg(
            sa.func.nullif(UptimeMetric.response_time, 0)
        ).label('response_time')
        tries_sum = sa.func.sum(UptimeMetric.tries).label('tries')
        code_min = sa.func.min(UptimeMetric.status_code).label('status_code')
        query = db_session.query(floor_func.label('interval'),
                                 rt_avg,
                                 tries_sum,
                                 code_min,
                                 )
        query = query.filter(UptimeMetric.resource_id == resource_id)
        query = query.filter(UptimeMetric.start_interval >= since_when)
        query = query.group_by(floor_func)
        query = query.order_by(sa.desc(floor_func))
        return query

    @classmethod
    def uptime_for_resource(cls, request, filter_settings):
        delta = filter_settings['end_date'] - filter_settings['start_date']
        if delta < h.time_deltas.get('12h')['delta']:
            interval = '1m'
        elif delta <= h.time_deltas.get('3d')['delta']:
            interval = '5m'
        elif delta >= h.time_deltas.get('2w')['delta']:
            interval = '24h'
        else:
            interval = '1h'

        chart_config = {
            'parentAgg': {'config': {'interval': interval},
                          'type': 'time_histogram'},
            'aggs': [
                {'config': {'field': 'response_time', 'label': 'requests'},
                 'type': 'avg', 'id': 'response_time'},
            ]}

        index_names = es_index_name_limiter(
            start_date=filter_settings['start_date'],
            end_date=filter_settings['end_date'], ixtypes=['uptime'])

        result_dict = {
            'name': 'metrics',
            'chart_type': chart_config.get('chartType'),
            'parent_agg': chart_config['parentAgg'],
            'series': [],
            'system_labels': {},
            'groups': [],
            'rect_regions': [],
            'categories': []
        }

        if not index_names:
            return result_dict

        es_query = {
            'query': {'filtered': {'filter': {
                'and': [
                    {'terms': {
                        'resource_id': [filter_settings['resource'][0]]}},
                    {'range': {
                        'timestamp': {
                            'gte': filter_settings['start_date'],
                            'lte': filter_settings['end_date']}
                    }}]}}},
            'aggs': {'parent_agg': {
                'date_histogram': {
                    'field': 'timestamp',
                    'interval': interval,
                    'extended_bounds': {
                        'max': filter_settings['end_date'],
                        'min': filter_settings['start_date']},
                    'min_doc_count': 0}, 'aggs': {
                    'response_time': {'filter': {
                        'and': [
                            {'exists': {
                                'field': 'tags.response_time.numeric_values'}}]
                    },
                        'aggs': {'sub_agg': {'avg': {
                            'field': 'tags.response_time.numeric_values'}}
                        }
                    }
                }
            }
            }
        }

        result = request.es_conn.search(
            body=es_query, index=index_names, doc_type='log', size=0)

        plot_data = []
        for item in result['aggregations']['parent_agg']['buckets']:
            x_time = datetime.utcfromtimestamp(int(item['key']) / 1000)
            point = {"x": x_time}
            value = item['response_time']['sub_agg']['value']
            point['response_time'] = round(value, 3) if value else 0
            plot_data.append(point)
        result_dict['series'] = plot_data
        return result_dict

    @classmethod
    def check_for_alert(cls, resource, *args, **kwargs):
        """ Check for open uptime alerts. Create new one if nothing is found
        and send alerts """
        db_session = get_db_session(kwargs.get('db_session'))
        request = get_current_request()
        event_type = 'uptime_alert'
        metric = kwargs['metric']
        event = EventService.for_resource([resource.resource_id],
                                          event_type=Event.types[event_type],
                                          status=Event.statuses['active'])
        if event.first():
            log.info('ALERT: PROGRESS: %s %s' % (event_type, resource))
        else:
            log.warning('ALERT: OPEN: %s %s' % (event_type, resource))
            event_values = {"status_code": metric["status_code"],
                            "tries": metric['tries'],
                            "response_time": metric['response_time']}
            new_event = Event(resource_id=resource.resource_id,
                              event_type=Event.types[event_type],
                              status=Event.statuses['active'],
                              values=event_values)
            db_session.add(new_event)
            new_event.send_alerts(request=request, resource=resource)
