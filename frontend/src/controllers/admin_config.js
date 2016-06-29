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


angular.module('appenlight.plugins.ae_uptime_ce').controller('PluginUptimeCEConfigController',
    PluginUptimeCEConfigController);

PluginUptimeCEConfigController.$inject = ['pluginConfigsResource']

function PluginUptimeCEConfigController(pluginConfigsResource) {
    var vm = this;
    /**
     * this is used to cascade the data from plugin directive to lower controller
     * @param resource
     */
    vm.init = function (resource, section, name) {
        vm.section = section;
        vm.name = name;
        vm.plugin = null;
        vm.loadConfig();
    };

    vm.loadConfig = function () {
        pluginConfigsResource.query({
            plugin_name: vm.name,
            section: 'global',
        }, function (data) {
            if (data.length > 0) {
                vm.plugin = data[0];
            }
            else {
                vm.plugin = new pluginConfigsResource();
                vm.plugin.plugin_name = vm.name;
                vm.plugin.config = {'uptime_regions_map': []};
                vm.plugin.section = 'global';
            }
        });

    };

    vm.addNewLocation = function () {
        vm.plugin.config.uptime_regions_map.push({
            name: '',
            country: ''
        });
    };

    vm.removeLocation = function (existin_item) {
        vm.plugin.config.uptime_regions_map = _.filter(
            vm.plugin.config.uptime_regions_map, function (item) {
                return item !== existin_item;
            });
    };

    var formResponse = function (response) {
        if (response.status === 422) {
            setServerValidation(vm.pluginConfigForm,
                response.data);
        }
    };

    vm.saveSettings = function () {
        if (typeof vm.plugin.id !== 'undefined' && vm.plugin.id !== null) {
            vm.plugin.$update(null, null, formResponse);
        }
        else {
            vm.plugin.$save(null, null, formResponse);
        }
    }

}
