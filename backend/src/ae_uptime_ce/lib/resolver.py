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

import gevent
import logging

from gevent.resolver_ares import Resolver
from dogpile.cache import make_region

memory_region = make_region().configure(
    'dogpile.cache.memory',
    expiration_time=600
)

log = logging.getLogger(__name__)


class CachingResolverException(Exception):
    pass


class CachingResolver(Resolver):
    def __repr__(self):
        return '<gevent.resolver_thread.CachingResolver at 0x%x pool=%r>' % (
            id(self),
            self.pool)

    def gethostbyname(self, *args):
        @memory_region.cache_on_arguments()
        def _cached(*args):
            return super(CachingResolver, self).gethostbyname(*args)

        return _cached(*args)

    def gethostbyname_ex(self, *args):
        @memory_region.cache_on_arguments()
        def _cached(*args):
            return super(CachingResolver, self).gethostbyname_ex(*args)

        return _cached(*args)

    def getaddrinfo(self, *args, **kwargs):
        @memory_region.cache_on_arguments()
        def _cached(*args, **kwargs):
            with gevent.Timeout(5, False):
                return super(CachingResolver, self).getaddrinfo(*args, **kwargs)

        result = _cached(*args, **kwargs)
        if result is None:
            raise CachingResolverException('Cant resolve {}'.format(args))
        return result

    def gethostbyaddr(self, *args, **kwargs):
        @memory_region.cache_on_arguments()
        def _cached(*args, **kwargs):
            return super(CachingResolver, self).gethostbyaddr(*args, **kwargs)

        return _cached(*args, **kwargs)

    def getnameinfo(self, *args, **kwargs):
        @memory_region.cache_on_arguments()
        def _cached(*args, **kwargs):
            return super(CachingResolver, self).getnameinfo(*args, **kwargs)

        return _cached(*args, **kwargs)
