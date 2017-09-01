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


angular.module('appenlight.plugins.ae_uptime_ce').controller('PluginUptimeCEApplicationController',
    PluginUptimeCEApplicationController);

PluginUptimeCEApplicationController.$inject = ['pluginConfigsResource']

function PluginUptimeCEApplicationController(pluginConfigsResource) {
    var vm = this;
    /**
     * this is used to cascade the data from plugin directive to lower controller
     * @param resource
     */
    vm.init = function (resource, section, name) {
        vm.resource = resource;
        vm.section = section;
        vm.name = name;
        vm.plugin = null;
        vm.loadConfig();
    };

    vm.loadConfig = function () {
        pluginConfigsResource.query({
            resource_id: vm.resource.resource_id,
            plugin_name: vm.name
        }, function (data) {
            if (data.length > 0) {
                vm.plugin = data[0];
            }
            else {
                vm.plugin = new pluginConfigsResource();
                vm.plugin.plugin_name = vm.name;
                vm.plugin.config = {'uptime_url': ''};
                vm.plugin.section = 'resource';
                vm.plugin.resource_id = vm.resource.resource_id;
            }
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
