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


angular.module('appenlight.plugins.ae_uptime_ce').controller('PluginUptimeCEController',
    PluginUptimeCEController);

PluginUptimeCEController.$inject = ['$scope', '$location', 'applicationsPropertyResource', 'stateHolder', 'AeConfig']

function PluginUptimeCEController($scope, $location, applicationsPropertyResource, stateHolder, AeConfig) {
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
        if (stateHolder.AeUser.applications.length) {
            vm.resource = Number($location.search().resource);
            if (!vm.resource) {
                vm.resource = stateHolder.AeUser.applications[0].resource_id;
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

        applicationsPropertyResource.get({
            'resourceId': vm.resource,
            'key': 'uptime_graphs',
            "start_date": timeSpanToStartDate(vm.timeSpan.key)
        }, function (data) {
            vm.uptimeHistoryData = {
                json: data.series,
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
        console.log('$locationChangeSuccess UptimeController');
        if (vm.loading.uptime === false) {
            vm.determineStartState();
            vm.refreshData();
        }
    });

}
