// Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
    stateHolder.plugins.callables.push(function () {
        console.log('ae_uptime run()');
        AeConfig.topNav.menuDashboardsItems.push(
            {'sref': 'uptime', 'label': 'Uptime Statistics'}
        );

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
    });
}]);
