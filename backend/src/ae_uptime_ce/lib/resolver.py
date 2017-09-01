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
            with gevent.Timeout(20, False):
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
