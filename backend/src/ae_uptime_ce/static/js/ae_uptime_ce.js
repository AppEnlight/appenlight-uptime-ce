angular.module('appenlight.templates').run(['$templateCache', function($templateCache) {
  'use strict';

  $templateCache.put('/ae_uptime_ce/templates/admin_config.html',
    "<h2>Monitoring location names</h2>\n" +
    "\n" +
    "<p>You can set the country flags and location names specified in monitoring tools</p>\n" +
    "\n" +
    "<form class=\"form-horizontal\" ng-controller=\"PluginUptimeCEConfigController as ctrlr\" ng-init=\"ctrlr.init(null, plugin_ctrlr.section, tmpl.name)\">\n" +
    "\n" +
    "    <div class=\"form-group\" ng-repeat=\"location in ctrlr.plugin.config.uptime_regions_map track by $index\">\n" +
    "        <label class=\"control-label col-sm-4 col-lg-3\">\n" +
    "            Location {{ $index +1 }}\n" +
    "        </label>\n" +
    "        <div class=\"col-sm-7 col-lg-8 form-inline\">\n" +
    "            <input type=\"text\" ng-model=\"location.name\" class=\"form-control\" placeholder=\"Location name\">\n" +
    "            <input type=\"text\" ng-model=\"location.country\" class=\"form-control slim-input\" placeholder=\"Country code\">\n" +
    "                    <span class=\"dropdown\" data-uib-dropdown>\n" +
    "                        <a class=\"btn btn-danger btn-sm\" data-uib-dropdown-toggle><span class=\"fa fa-trash-o\"></span></a>\n" +
    "                      <ul class=\"dropdown-menu\">\n" +
    "                          <li><a>No</a></li>\n" +
    "                          <li><a ng-click=\"ctrlr.removeLocation(location)\">Yes</a></li>\n" +
    "                      </ul>\n" +
    "                    </span>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "\n" +
    "    <a class=\"btn btn-default\" ng-click=\"ctrlr.addNewLocation()\"><span class=\"fa fa-plus-circle\"></span> Add another location</a>\n" +
    "    <a class=\"btn btn-info\" ng-click=\"ctrlr.saveSettings()\">Save plugin settings</a>\n" +
    "</form>\n"
  );


  $templateCache.put('/ae_uptime_ce/templates/application_update.html',
    "<div class=\"form-group\" ng-controller=\"PluginUptimeCEApplicationController as ctrlr\" ng-init=\"ctrlr.init(plugin_ctrlr.resource, plugin_ctrlr.section, tmpl.name)\">\n" +
    "    <form name=\"ctrlr.pluginConfigForm\"></form>\n" +
    "    <data-form-errors errors=\"ctrlr.pluginConfigForm.ae_validation.uptime_url\"></data-form-errors>\n" +
    "    <label class=\"control-label col-sm-4 col-lg-3\">\n" +
    "        Application URL\n" +
    "    </label>\n" +
    "    <div class=\" col-sm-8 col-lg-9 \">\n" +
    "        <input class=\"form-control\"  name=\"uptime_url\" placeholder=\"http://somedomain.com\" type=\"text\" ng-model=\"ctrlr.plugin.config.uptime_url\">\n" +
    "        <p class=\"description\">Required for uptime monitoring</p>\n" +
    "    </div>\n" +
    "\n" +
    "    <a class=\"btn btn-info\" ng-click=\"ctrlr.saveSettings()\">Save plugin settings</a>\n" +
    "\n" +
    "</div>\n"
  );


  $templateCache.put('/ae_uptime_ce/templates/uptime.html',
    "<div ng-if=\"!AeUser.applications.length\" class=\"ng-hide\">\n" +
    "    <div ng-include=\"'templates/quickstart.html'\"></div>\n" +
    "</div>\n" +
    "\n" +
    "<ng-include src=\"'templates/loader.html'\" ng-if=\"uptime.loading.uptime\"></ng-include>\n" +
    "\n" +
    "<div ng-if=\"AeUser.applications.length\">\n" +
    "\n" +
    "    <div ng-if=\"!uptime.loading.uptime\">\n" +
    "\n" +
    "\n" +
    "        <div class=\"alert alert-warning\">\n" +
    "            This section is currently in <strong>BETA</strong>. You an expect changes to functionality and usability improvements.\n" +
    "            We encourage you to send us feedback and ideas for new functionality.\n" +
    "        </div>\n" +
    "\n" +
    "        <div class=\"row\">\n" +
    "            <div class=\"col-sm-12\">\n" +
    "                <div class=\"panel\">\n" +
    "                    <div class=\"panel-body \">\n" +
    "                        <p class=\"form-inline\">\n" +
    "                            <select ng-model=\"uptime.resource\" ng-change=\"uptime.updateSearchParams()\" ng-options=\"r.resource_id as r.resource_name for r in AeUser.applications\" class=\"SelectField form-control input-sm slim-input\"></select>\n" +
    "\n" +
    "                            <select class=\"SelectField form-control input-sm\" ng-model=\"uptime.timeSpan\"\n" +
    "                                    ng-options=\"i as i.label for i in uptime.timeOptions | objectToOrderedArray:'minutes'\" ng-change=\"uptime.updateSearchParams()\"\n" +
    "                                    class=\"SelectField\"></select>\n" +
    "                        </p>\n" +
    "\n" +
    "                        <c3chart data-domid=\"uptime_history_chart\" data-data=\"uptime.uptimeHistoryData\" data-config=\"uptime.uptimeHistoryConfig\" ng-if=\"!uptime.loading.uptimeCharts\">\n" +
    "                        </c3chart>\n" +
    "\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "        <div class=\"row\" ng-if=\"!uptime.loading.uptime\">\n" +
    "            <div class=\"col-sm-8\">\n" +
    "                <div class=\"panel panel-default\">\n" +
    "                    <table class=\"table table-striped uptime-list\">\n" +
    "                        <caption>Todays uptime</caption>\n" +
    "                        <thead>\n" +
    "                        <tr>\n" +
    "                            <th class=\"c1 interval\">When</th>\n" +
    "                            <th class=\"c2 avg_response\">Average response time</th>\n" +
    "                            <th class=\"c3 http_status\">HTTP Status</th>\n" +
    "                            <th class=\"c4 retries\">Retries</th>\n" +
    "                            <th class=\"c5 location\">Location</th>\n" +
    "                        </tr>\n" +
    "                        </thead>\n" +
    "                        <tbody>\n" +
    "                        <tr>\n" +
    "                            <td colspan=\"5\" class=\"p-a-0\">\n" +
    "                                <div style=\"max-height: 400px; overflow-y: auto\">\n" +
    "                                    <table class=\"table table-striped\">\n" +
    "                                        <tr ng-repeat=\"entry in uptime.latestStats track by entry.id\" class=\"{{(entry.status_code == 0 || entry.status_code >= 400) ? 'problem' : ''}}\">\n" +
    "                                            <td class=\"c1 interval\">\n" +
    "                                                {{entry.interval.replace('T', ' ').slice(0,16)}}\n" +
    "                                            </td>\n" +
    "                                            <td class=\"c2 avg_response\">{{entry.avg_response_time}}s</td>\n" +
    "                                            <td class=\"c3 http_status\">{{entry.status_code}} {{(entry.http_status == 0 || entry.http_status >= 400) ? 'Problem' : ''}}</td>\n" +
    "                                            <td class=\"c4 retries\">{{entry.retries}}</td>\n" +
    "                                            <td class=\"c5 location\"><img ng-src=\"/static/appenlight/images/icons/countries/{{entry.location.country}}.png\"/> {{entry.location.city}}</td>\n" +
    "                                        </tr>\n" +
    "                                    </table>\n" +
    "                                </div>\n" +
    "                            </td>\n" +
    "                        </tr>\n" +
    "                        </tbody>\n" +
    "                    </table>\n" +
    "                </div>\n" +
    "\n" +
    "            </div>\n" +
    "            <div class=\"col-sm-4\">\n" +
    "\n" +
    "\n" +
    "                <div class=\"panel\">\n" +
    "                    <div class=\"panel-body\">\n" +
    "                        <p>Uptime for last {{uptime.timeSpan.label}}</p>\n" +
    "\n" +
    "                        <c3chart data-domid=\"uptime_gauge\" data-data=\"uptime.uptimeGaugeData\" data-config=\"uptime.uptimeGaugeConfig\" ng-if=\"!uptime.loading.uptime\">\n" +
    "                        </c3chart>\n" +
    "\n" +
    "                    </div>\n" +
    "                </div>\n" +
    "\n" +
    "                <div class=\"panel panel-default\">\n" +
    "                    <table class=\"table table-striped uptime-list\">\n" +
    "                        <caption>This month's uptime</caption>\n" +
    "                        <thead>\n" +
    "                        <tr>\n" +
    "                            <th class=\"c1 interval\">When</th>\n" +
    "                            <th class=\"c2 avg_response\">Average response time</th>\n" +
    "                            <th class=\"c3 retries\">Retries</th>\n" +
    "                        </tr>\n" +
    "                        </thead>\n" +
    "                        <tbody>\n" +
    "                        <tr>\n" +
    "                            <td colspan=\"3\" class=\"p-a-0\">\n" +
    "                                <div style=\"max-height: 600px; overflow-y: auto\">\n" +
    "                                    <table class=\"table table-striped m-a-0\">\n" +
    "                                        <tr ng-repeat=\"entry in uptime.monthlyStats track by entry.id\">\n" +
    "                                            <td class=\"c1 interval\">\n" +
    "                                                {{entry.interval.replace('T', ' ').slice(0,16)}}\n" +
    "                                            </td>\n" +
    "                                            <td class=\"c2 avg_response\">{{entry.avg_response_time}}s</td>\n" +
    "                                            <td class=\"c3 retries\">{{entry.retries}}</td>\n" +
    "                                        </tr>\n" +
    "                                    </table>\n" +
    "                                </div>\n" +
    "                            </td>\n" +
    "                        </tr>\n" +
    "                        </tbody>\n" +
    "                    </table>\n" +
    "                </div>\n" +
    "\n" +
    "            </div>\n" +
    "        </div>\n" +
    "\n" +
    "\n" +
    "    </div>\n" +
    "</div>\n"
  );

}]);

;// # Copyright (C) 2010-2016  RhodeCode GmbH
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
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.plugins.ae_uptime_ce', []).config(['$stateProvider', function ($stateProvider) {
    $stateProvider.state('uptime', {
        url: '/ui/uptime',
        templateUrl: '/ae_uptime_ce/templates/uptime.html',
        controller: 'PluginUptimeCEController as uptime'
    });
}]).run(['stateHolder', function (stateHolder) {
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
    
}]);

;// # Copyright (C) 2010-2016  RhodeCode GmbH
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
// # App Enlight Enterprise Edition, including its added features, Support
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

;// # Copyright (C) 2010-2016  RhodeCode GmbH
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
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/


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

;// # Copyright (C) 2010-2016  RhodeCode GmbH
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
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/


angular.module('appenlight.plugins.ae_uptime_ce').controller('PluginUptimeCEController',
    PluginUptimeCEController);

PluginUptimeCEController.$inject = ['$scope', '$location', 'applicationsPropertyResource', 'AeUser', 'AeConfig']

function PluginUptimeCEController($scope, $location, applicationsPropertyResource, AeUser, AeConfig) {
    var vm = this;
    vm.timeOptions = {};
    var allowed = ['1h', '4h', '12h', '24h', '3d', '1w', '2w', '1M'];
    _.each(allowed, function (key) {
        if (allowed.indexOf(key) !== -1) {
            vm.timeOptions[key] = AeConfig.timeOptions[key];
        }
    });

    vm.uptimeGaugeData = {
        columns: [['uptime', 0]]
    };
    vm.uptimeGaugeConfig = {
        data: {
            columns: [['uptime', 0]],
            type: 'gauge'
        },
        gauge: {
            label: {
                show: false, // to turn off the min/max labels.
                format: function (value, ratio) {
                    return value + '%';
                }
            },
            min: 90, // 0 is default, //can handle negative min e.g. vacuum / voltage / current flow / rate of change
            max: 100, // 100 is default
            units: ' %',
            width: 15 // for adjusting arc thickness
        },
        color: {
            pattern: ['#FF0000', '#F97600', '#F6C600', '#60B044'], // the three color levels for the percentage values.
            threshold: {
                values: [98, 99.5, 100]
            }
        },
        size: {
            height: 195
        }
    };

    vm.uptimeHistoryConfig = {
        data: {
            json: [],
            xFormat: '%Y-%m-%dT%H:%M:%S',
            names: {
                y: 'Average response time'
            },
        },
        color: {
            pattern: ['#6baed6', '#e6550d', '#74c476', '#fdd0a2', '#8c564b']
        },
        point: {
            show: false
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    culling: {
                        max: 10 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
                }
            },
            y: {
                tick: {
                    count: 5,
                    format: d3.format('.2f')
                }
            }
        },
        subchart: {
            show: true,
            size: {
                height: 20
            }
        },
        size: {
            height: 250
        },
        zoom: {
            rescale: true
        },
        grid: {
            x: {
                show: true
            },
            y: {
                show: true
            }
        },
        tooltip: {
            format: {
                title: function (d) {
                    return '' + d;
                },
                value: function (v) {
                    return v
                }
            }
        }
    };
    vm.uptimeHistoryData = {};


    vm.loading = {uptime: true, uptimeCharts: true};

    vm.today = function () {
        vm.pickerDate = new Date();
    };

    vm.latestStats = [];
    vm.monthlyStats = [];
    vm.currentUptime = [];
    vm.seriesUptimeData = [];

    vm.determineStartState = function () {
        if (AeUser.applications.length) {
            vm.resource = Number($location.search().resource);
            if (!vm.resource) {
                vm.resource = AeUser.applications[0].resource_id;
                $location.search('resource', vm.resource);
            }
        }
        var timespan = $location.search().timespan;
        if (_.has(vm.timeOptions, timespan)) {
            vm.timeSpan = vm.timeOptions[timespan];
        }
        else {
            vm.timeSpan = vm.timeOptions['1h'];
        }
    };

    vm.updateSearchParams = function () {
        $location.search('resource', vm.resource);
        $location.search('timespan', vm.timeSpan.key);
    };

    vm.loadStats = function () {
        vm.loading.uptime = true;
        applicationsPropertyResource.get({
            'resourceId': $location.search().resource,
            'key': 'uptime',
            "start_date": timeSpanToStartDate(vm.timeSpan.key)
        }, function (data) {
            vm.currentUptime = data.current_uptime;
            vm.latestStats = data.latest_stats;
            vm.monthlyStats = data.monthly_stats;

            vm.uptimeGaugeData = {
                columns: [
                    ['uptime', data.current_uptime]
                ],
                type: 'gauge'
            };

            vm.loading.uptime = false;
        });
    };

    vm.fetchUptimeMetrics = function () {
        vm.loading.uptimeCharts = true;

        applicationsPropertyResource.query({
            'resourceId': vm.resource,
            'key': 'uptime_graphs',
            "start_date": timeSpanToStartDate(vm.timeSpan.key)
        }, function (data) {
            vm.uptimeHistoryData = {
                json: data,
                keys: {
                    x: 'x',
                    value: ["response_time"]
                }
            };
            vm.loading.uptimeCharts = false;
        });
    };

    vm.refreshData = function () {
        if (vm.resource) {
            vm.loadStats();
            vm.fetchUptimeMetrics();
        }
    };

    vm.today();
    vm.determineStartState();
    vm.refreshData();

    $scope.$on('$locationChangeSuccess', function () {
        
        if (vm.loading.uptime === false) {
            vm.determineStartState();
            vm.refreshData();
        }
    });

}
