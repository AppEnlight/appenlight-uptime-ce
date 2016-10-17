// # Copyright (C) 2010-2016  RhodeCode GmbH
// #
// # This program is free software: you can redistribute it and/or modify
// # it under the terms of the GNU Affero General Public License, version 3
// # (only), as published by the Free Software Foundation.
// #
// # This program is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU Affero General Public License
// # along with this program.  If not, see <http://www.gnu.org/licenses/>.
// #
// # This program is dual-licensed. If you wish to learn more about the
// # AppEnlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.plugins.ae_uptime_ce', []).config(['$stateProvider', function ($stateProvider) {
    $stateProvider.state('uptime', {
        url: '/ui/uptime',
        templateUrl: '/ae_uptime_ce/templates/uptime.html',
        controller: 'PluginUptimeCEController as uptime'
    });
}]).run(['stateHolder', 'AeConfig', function (stateHolder, AeConfig) {
    /**
     * register plugin in stateHolder
     */
    stateHolder.plugins.addInclusion('application.update',
        {
            name: 'ae_uptime_ce',
            template: '/ae_uptime_ce/templates/application_update.html'
        }
    );
    stateHolder.plugins.addInclusion('admin.config',
        {
            name: 'ae_uptime_ce',
            template: '/ae_uptime_ce/templates/admin_config.html'
        }
    );

    AeConfig.topNav.menuDashboardsItems.push(
        {'sref': 'uptime', 'label': 'Uptime Statistics'}
    );
}]);
