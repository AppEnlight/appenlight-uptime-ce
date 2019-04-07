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

import sqlalchemy as sa
from appenlight.models import Base
from ziggurat_foundations.models.base import BaseModel


class UptimeMetric(Base, BaseModel):
    __tablename__ = "ae_uptime_ce_metrics"
    __table_args__ = {"implicit_returning": False}

    id = sa.Column(sa.BigInteger(), primary_key=True)
    resource_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("applications.resource_id"),
        nullable=False,
        primary_key=True,
    )
    start_interval = sa.Column(sa.DateTime(), nullable=False, primary_key=True)
    response_time = sa.Column(sa.Float, nullable=False, default=0)
    status_code = sa.Column(sa.Integer, default=0)
    tries = sa.Column(sa.Integer, default=1)
    is_ok = sa.Column(sa.Boolean, default=True)
    owner_user_id = sa.Column(sa.Integer(), sa.ForeignKey("users.id"), nullable=True)
    location = sa.Column(sa.Integer, default=1)

    @property
    def partition_id(self):
        return "rcae_uptime_ce_%s" % self.start_interval.strftime("%Y_%m")

    def es_doc(self):
        return {
            "uptime_id": self.id,
            "resource_id": self.resource_id,
            "timestamp": self.start_interval,
            "permanent": True,
            "request_id": None,
            "log_level": "INFO",
            "message": None,
            "namespace": "appenlight.uptime",
            "tags": {
                "response_time": {
                    "values": self.response_time,
                    "numeric_values": self.response_time,
                },
                "status_code": {
                    "values": self.status_code,
                    "numeric_values": self.status_code,
                },
                "tries": {"values": self.tries, "numeric_values": self.tries},
                "is_ok": {"values": self.is_ok, "numeric_values": int(self.is_ok)},
                "owner_user_id": {
                    "values": self.owner_user_id,
                    "numeric_values": self.owner_user_id,
                },
                "location": {"values": self.location, "numeric_values": self.location},
            },
            "tag_list": [
                "response_time",
                "status_code",
                "tries",
                "is_ok",
                "owner_user_id",
                "location",
            ],
        }
