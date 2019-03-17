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

from datetime import datetime, timedelta

from celery.utils.log import get_task_logger
from zope.sqlalchemy import mark_changed

from appenlight.celery import celery
from appenlight.lib import print_traceback
from appenlight.lib.utils import parse_proto
from appenlight.lib.utils.date_utils import convert_date
from appenlight.models import DBSession, Datastores
from appenlight.models.event import Event
from appenlight.models.services.application import ApplicationService
from appenlight.models.services.event import EventService
from ae_uptime_ce.models.uptime_metric import UptimeMetric
from ae_uptime_ce.models.services.uptime_metric import UptimeMetricService

log = get_task_logger(__name__)


@celery.task(queue="metrics", default_retry_delay=600, max_retries=999)
def add_uptime_stats(params, metric):
    proto_version = parse_proto(params.get("protocol_version"))
    try:
        application = ApplicationService.by_id_cached()(metric["resource_id"])
        application = DBSession.merge(application, load=False)
        if not application:
            return
        start_interval = convert_date(metric["timestamp"])
        start_interval = start_interval.replace(second=0, microsecond=0)
        new_metric = UptimeMetric(
            start_interval=start_interval,
            response_time=metric["response_time"],
            status_code=metric["status_code"],
            is_ok=metric["is_ok"],
            location=metric.get("location", 1),
            tries=metric["tries"],
            resource_id=application.resource_id,
            owner_user_id=application.owner_user_id,
        )
        DBSession.add(new_metric)
        DBSession.flush()
        add_metrics_uptime([new_metric.es_doc()])
        if metric["is_ok"]:
            event_types = [Event.types["uptime_alert"]]
            statuses = [Event.statuses["active"]]
            # get events older than 5 min
            events = EventService.by_type_and_status(
                event_types,
                statuses,
                older_than=(datetime.utcnow() - timedelta(minutes=6)),
                app_ids=[application.resource_id],
            )
            for event in events:
                event.close()
        else:
            UptimeMetricService.check_for_alert(application, metric=metric)
        action = "METRICS UPTIME"
        metrics_msg = "%s: %s, proto:%s" % (action, str(application), proto_version)
        log.info(metrics_msg)
        session = DBSession()
        mark_changed(session)
        return True
    except Exception as exc:
        print_traceback(log)
        add_uptime_stats.retry(exc=exc)


def add_metrics_uptime(es_docs):
    for doc in es_docs:
        partition = "rcae_u_%s" % doc["timestamp"].strftime("%Y_%m")
        Datastores.es.index(partition, "log", doc)
