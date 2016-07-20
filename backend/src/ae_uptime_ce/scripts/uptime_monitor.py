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

from gevent import monkey

monkey.patch_all()

import argparse
import configparser
import logging

from datetime import datetime

import gevent
import requests

from gevent.lock import RLock
from ae_uptime_ce.lib.ext_json import json

logging.basicConfig(level=logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

try:
    requests.packages.urllib3.disable_warnings()
except Exception:
    pass

APPS_TO_CHECK = {}
CONFIG = {}


def sync_apps():
    log.info('Syncing monitored url list')
    headers = {'x-appenlight-auth-token': CONFIG['api_key'],
               "Content-type": "application/json",
               'User-Agent': 'Appenlight/ping-service'}
    try:
        resp = requests.get(CONFIG['sync_url'], headers=headers,
                            timeout=10)
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
        if app['url']:
            APPS_TO_CHECK[app['id']] = app['url']
            active_app_ids.append(app['id'])
    log.info('Active applications found {}'.format(len(active_app_ids)))
    for app_id in list(APPS_TO_CHECK.keys()):
        if app_id not in active_app_ids:
            # means someone turned off monitoring
            APPS_TO_CHECK.pop(app_id, None)


last_sync = datetime.utcnow()


def check_response(app_id):
    log.debug('checking response for: {}'.format(app_id))
    current_time = datetime.utcnow()
    tries = 1
    while tries < 3:
        headers = {'x-appenlight-auth-token': CONFIG['api_key'],
                   "Content-type": "application/json",
                   'User-Agent': 'Appenlight/ping-service'}
        try:
            resp = requests.get(
                APPS_TO_CHECK[app_id],
                headers={'User-Agent': 'Appenlight/ping-service'},
                timeout=20, verify=False)
            is_ok = resp.status_code == requests.codes.ok
            elapsed = resp.elapsed.total_seconds()
            status_code = resp.status_code
            break
        except requests.exceptions.Timeout:
            is_ok = False
            elapsed = 0
            status_code = 0
        except requests.exceptions.RequestException:
            is_ok = False
            elapsed = 0
            status_code = 0
        tries += 1

    log.info('app:{} url:{} status:{} time:{} tries:{}'.format(
        app_id, APPS_TO_CHECK[app_id], status_code, elapsed, tries))
    try:
        json_data = json.dumps(
            {'resource': app_id,
             "is_ok": is_ok,
             "response_time": elapsed,
             'timestamp': current_time,
             'status_code': status_code,
             'location': CONFIG['location'],
             'tries': tries})
        result = requests.post(CONFIG['update_url'], data=json_data,
                               headers=headers, timeout=30)
        if result.status_code != requests.codes.ok:
            log.error('communication problem, {}'.format(result.status_code))
    except requests.exceptions.RequestException as exc:
        log.error(str(exc))


def sync_forever():
    try:
        sync_apps()
    finally:
        gevent.spawn_later(20, sync_forever)


def check_forever():
    log.info('Spawning new checks')
    try:
        for app_id in APPS_TO_CHECK.keys():
            gevent.spawn(check_response, app_id)
    finally:
        gevent.spawn_later(60, check_forever)


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
    gevent.spawn_later(10, check_forever)
    while True:
        gevent.sleep(0.5)

if __name__ == '__main__':
    main()
