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

import sqlalchemy as sa
from appenlight.models import Base
from ziggurat_foundations.models.base import BaseModel


class UptimeMetric(Base, BaseModel):
    __tablename__ = 'ae_uptime_ce_metrics'
    __table_args__ = {'implicit_returning': False}

    id = sa.Column(sa.BigInteger(), primary_key=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('applications.resource_id'),
                            nullable=False, primary_key=True)
    start_interval = sa.Column(sa.DateTime(), nullable=False, primary_key=True)
    response_time = sa.Column(sa.Float, nullable=False, default=0)
    status_code = sa.Column(sa.Integer, default=0)
    tries = sa.Column(sa.Integer, default=1)
    is_ok = sa.Column(sa.Boolean, default=True)
    owner_user_id = sa.Column(sa.Integer(), sa.ForeignKey('users.id'),
                              nullable=True)
    location = sa.Column(sa.Integer, default=1)

    @property
    def partition_id(self):
        return 'rcae_u_%s' % self.start_interval.strftime('%Y_%m')

    def es_doc(self):
        return {
            'resource_id': self.resource_id,
            'timestamp': self.start_interval,
            'permanent': True,
            'request_id': None,
            'log_level': 'INFO',
            'message': None,
            'namespace': 'appenlight.uptime',
            'tags': {
                'response_time': {'values': self.response_time,
                                  'numeric_values': self.response_time},
                'status_code': {'values': self.status_code,
                                'numeric_values': self.status_code},
                'tries': {'values': self.tries,
                          'numeric_values': self.tries},
                'is_ok': {'values': self.is_ok,
                          'numeric_values': int(self.is_ok)},
                'owner_user_id': {'values': self.owner_user_id,
                                  'numeric_values': self.owner_user_id},
                'location': {'values': self.location,
                             'numeric_values': self.location},
            },
            'tag_list': ['response_time', 'status_code', 'tries', 'is_ok',
                         'owner_user_id', 'location']
        }
