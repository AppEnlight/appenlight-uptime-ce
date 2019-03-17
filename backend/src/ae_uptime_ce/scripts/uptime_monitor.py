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
from gevent import monkey

gevent.config.resolver = [
    'ae_uptime_ce.lib.resolver.CachingResolver',
    'gevent.resolver_ares.Resolver',
    'gevent.resolver_thread.Resolver',
    'gevent.socket.BlockingResolver']
monkey.patch_all()

import argparse
import configparser
import logging

from datetime import datetime

import requests

from gevent.queue import Queue, Empty

from ae_uptime_ce.lib.ext_json import json
from ae_uptime_ce.lib.resolver import CachingResolverException

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
root_log = logging.getLogger()
root_log.setLevel(logging.INFO)
root_log.handlers[0].setFormatter(formatter)
logging.getLogger('requests').setLevel(logging.WARNING)
# create console handler with a higher log level
log = logging.getLogger(__name__)

try:
    requests.packages.urllib3.disable_warnings()
except Exception:
    pass

APPS_TO_CHECK = {}
CONFIG = {}

RESPONSE_QUEUE = Queue()


def sync_apps():
    """ Periodically grabs the application list from server"""

    log.info('Syncing monitored url list')
    headers = {'x-appenlight-auth-token': CONFIG['api_key'],
               "Content-type": "application/json",
               'User-Agent': 'Appenlight/ping-service'}
    try:
        resp = requests.get(CONFIG['sync_url'], headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        log.error(str(exc))
        return
    active_app_ids = []
    apps = resp.json()
    log.info('Total applications found {}'.format(len(apps)))
    for app in apps:
        # update urls
        log.debug('processing app: {}'.format(app))
        if app['url'].strip():
            APPS_TO_CHECK[app['id']] = {'url': app['url'],
                                        'session': requests.Session(),
                                        'ip': None}
            active_app_ids.append(app['id'])
    log.info('Active applications found {}'.format(len(active_app_ids)))
    for app_id in list(APPS_TO_CHECK.keys()):
        if app_id not in active_app_ids:
            # means someone turned off monitoring
            APPS_TO_CHECK.pop(app_id, None)


last_sync = datetime.utcnow()


def check_response(app_id):
    """ Checks response for specific url """
    url = APPS_TO_CHECK[app_id]['url']
    session = APPS_TO_CHECK[app_id]['session']
    current_time = datetime.utcnow()
    tries = 1
    while tries < 3:
        log.debug('checking response for: {} {}'.format(app_id, url))
        start_time = datetime.utcnow()
        is_ok = False
        elapsed = 0
        status_code = 0
        try:
            resp = session.get(
                url,
                headers={'User-Agent': 'Appenlight/ping-service'},
                timeout=20, verify=False)
            is_ok = resp.status_code == requests.codes.ok
            elapsed = resp.elapsed.total_seconds()
            status_code = resp.status_code
            break
        except (requests.exceptions.Timeout,
                requests.exceptions.RequestException,
                CachingResolverException
                ) as exc:
            log.info(exc)
        tries += 1

    log.info('app:{} url:{} status:{} time:{} tries:{}'.format(
        app_id, url, status_code, elapsed, tries))
    RESPONSE_QUEUE.put({'resource_id': app_id,
                        "is_ok": is_ok,
                        "response_time": elapsed,
                        'timestamp': current_time,
                        'status_code': status_code,
                        'location': CONFIG['location'],
                        'tries': tries})


def sync_forever():
    try:
        sync_apps()
    finally:
        gevent.spawn_later(20, sync_forever)


def check_forever():
    log.info('Spawning new checks')
    for app_id in APPS_TO_CHECK:
        gevent.spawn_later(0.1, check_response, app_id)
    gevent.spawn_later(60, check_forever)


def report_forever():
    """ Sends response info back to AppEnlight """
    headers = {'x-appenlight-auth-token': CONFIG['api_key'],
               "Content-type": "application/json",
               'User-Agent': 'Appenlight/ping-service'}
    try:
        reported = []
        while True:
            try:
                reported.append(RESPONSE_QUEUE.get(timeout=5))
            except Empty:
                break
        while reported:
            log.info('Reporting data back to AppEnlight')
            try:
                result = requests.post(CONFIG['update_url'],
                                       data=json.dumps(reported[:500]),
                                       headers=headers, timeout=30)
                if result.status_code != requests.codes.ok:
                    log.error('communication problem, {}'.format(
                        result.status_code))
            except requests.exceptions.RequestException as exc:
                log.error(str(exc))
            reported = reported[500:]
    finally:
        gevent.spawn_later(5, report_forever)


default_sync_url = 'http://127.0.0.1:6543/api/uptime_app_list'
default_update_url = 'http://127.0.0.1:6543/api/uptime'
default_location = '1'


def main():
    parser = argparse.ArgumentParser(description='AppEnlight Uptime Monitor')
    parser.add_argument('-c', '--config',
                        help='Configuration ini file')
    parser.add_argument('-s', '--sync-url',
                        default=default_sync_url,
                        help='Source URL for application url list')
    parser.add_argument('-u', '--update-url',
                        default=default_update_url,
                        help='Destination URL for uptime reporting')
    parser.add_argument('-l', '--location',
                        default=default_location,
                        help='Integer identifier for location of ping service')
    parser.add_argument('-k', '--api-key',
                        help='API token(key) for the root user that lists')

    args = parser.parse_args()
    if args.config:
        parser = configparser.ConfigParser({
            'sync_url': default_sync_url,
            'update_url': default_update_url,
            'location': default_location,
        })
        parser.read(args.config)
        CONFIG['sync_url'] = parser.get('appenlight_uptime', 'sync_url')
        CONFIG['update_url'] = parser.get('appenlight_uptime', 'update_url')
        CONFIG['location'] = parser.get('appenlight_uptime', 'location')
        CONFIG['api_key'] = parser.get('appenlight_uptime', 'api_key')
    else:
        CONFIG['sync_url'] = args.sync_url
        CONFIG['update_url'] = args.update_url
        CONFIG['location'] = args.location
        CONFIG['api_key'] = args.api_key

    CONFIG['location'] = int(CONFIG['location'])
    if not CONFIG['api_key']:
        raise Exception('API token is not set')
    log.info('Starting uptime monitor, location: {}'.format(
        CONFIG['location']))
    log.info('Sending to: {}'.format(CONFIG['update_url']))
    log.info('Syncing info from: {}'.format(CONFIG['update_url']))
    sync_forever()
    report_forever()
    gevent.spawn_later(5, check_forever)
    while True:
        gevent.sleep(0.5)


if __name__ == '__main__':
    main()
