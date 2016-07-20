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
# AppEnlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

from datetime import datetime, timedelta

from celery.utils.log import get_task_logger
from zope.sqlalchemy import mark_changed

from appenlight.celery import celery
from appenlight.lib import print_traceback
from appenlight.lib.utils.date_utils import convert_date
from appenlight.models import DBSession, Datastores
from appenlight.models.event import Event
from appenlight.models.services.application import ApplicationService
from appenlight.models.services.event import EventService
from ae_uptime_ce.models.uptime_metric import UptimeMetric
from ae_uptime_ce.models.services.uptime_metric import \
    UptimeMetricService

log = get_task_logger(__name__)


@celery.task(queue="metrics", default_retry_delay=600, max_retries=999)
def add_uptime_stats(request, metric, environ=None, **kwargs):
    proto_version = request.get('protocol_version')
    if proto_version:
        try:
            proto_version = float(proto_version)
        except (ValueError, TypeError) as exc:
            proto_version = None
    try:
        application = ApplicationService.by_id_cached()(metric['resource_id'])
        application = DBSession.merge(application, load=False)
        if not application:
            return
        start_interval = convert_date(metric['timestamp'])
        start_interval = start_interval.replace(second=0, microsecond=0)
        new_metric = UptimeMetric(
            start_interval=start_interval,
            response_time=metric['response_time'],
            status_code=metric['status_code'],
            is_ok=metric['is_ok'],
            location=metric.get('location', 1),
            tries=metric['tries'],
            resource_id=application.resource_id,
            owner_user_id=application.owner_user_id)
        DBSession.add(new_metric)
        DBSession.flush()
        add_metrics_uptime([new_metric.es_doc()])
        if metric['is_ok']:
            event_types = [Event.types['uptime_alert']]
            statuses = [Event.statuses['active']]
            # get events older than 5 min
            events = EventService.by_type_and_status(
                event_types,
                statuses,
                older_than=(datetime.utcnow() - timedelta(minutes=6)),
                app_ids=[application.resource_id])
            for event in events:
                event.close()
        else:
            UptimeMetricService.check_for_alert(application,
                                                metric=metric)
        action = 'METRICS UPTIME'
        metrics_msg = '%s: %s, proto:%s' % (
            action,
            str(application),
            proto_version
        )
        log.info(metrics_msg)
        session = DBSession()
        mark_changed(session)
        return True
    except Exception as exc:
        print_traceback(log)
        add_uptime_stats.retry(exc=exc)


def add_metrics_uptime(es_docs):
    for doc in es_docs:
        partition = 'rcae_u_%s' % doc['timestamp'].strftime('%Y_%m')
        Datastores.es.index(partition, 'log', doc)
