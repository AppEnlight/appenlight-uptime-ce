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
import datetime
from collections import defaultdict
from appenlight.scripts.reindex_elasticsearch import detect_tables
from ae_uptime_ce.models.uptime_metric import UptimeMetric
from appenlight.models import (
    DBSession,
    Datastores
)

log = logging.getLogger(__name__)

def reindex_uptime():
    try:
        Datastores.es.delete_index('rcae_u*')
    except Exception as e:
        print(e)

    log.info('reindexing uptime')
    i = 0
    task_start = datetime.datetime.now()
    uptime_tables = detect_tables('uptime_ce_metrics_p_')
    for partition_table in uptime_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                i += 1
                item = UptimeMetric(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round  {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'log', v)

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))
