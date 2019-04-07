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
import datetime
from collections import defaultdict
import elasticsearch.exceptions
import elasticsearch.helpers

from appenlight.scripts.reindex_elasticsearch import detect_tables
from ae_uptime_ce.models.uptime_metric import UptimeMetric
from appenlight.models import DBSession, Datastores

log = logging.getLogger(__name__)


def reindex_uptime():
    try:
        Datastores.es.indices.delete("rcae_uptime_ce_*")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    log.info("reindexing uptime")
    i = 0
    task_start = datetime.datetime.now()
    uptime_tables = detect_tables("ae_uptime_ce_metrics_p_")
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
                log.info("round  {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "log"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))
