var fs = require('fs');
var ini = require('ini');
var config = ini.parse(fs.readFileSync('./locations.ini', 'utf-8'))

module.exports = function (grunt) {
    var packageInfo = grunt.file.readJSON('package.json');
    var grunt_conf_obj = {
        pkg: packageInfo,

        ngtemplates: {
            app: {
                options: {
                    prefix: '/ae_uptime_ce',
                    module: 'appenlight.templates'
                },
                cwd: 'src',
                src: '**/*.html',
                dest: 'build/' + packageInfo.name + '_templates.js'
            }
        },

        concat: {
            options: {
                // define a string to put between each file in the concatenated output
                separator: '\n;'
            },
            dev: {
                src: [
                    'build/' + packageInfo.name + '_templates.js',
                    'src/app.js',
                    'src/**/*.js',
                    '!src/**/*_test.js'
                ],
                dest: 'build/' + packageInfo.name + '.js',
                nonull: true
            },
            dist: {
                src: [
                    'build/' + packageInfo.name + '.js'
                ],
                dest: 'build/release/js/' + packageInfo.name + '.js',
                nonull: true
            },
        },
        removelogging: {
            dist: {
                src: 'build/' + packageInfo.name + '.js'
            }
        },
        copy: {
            css: {
                files: [
                    // includes files within path and its sub-directories
                    {
                        expand: true,
                        cwd: 'build/release/css',
                        src: ['front.css'],
                        dest: '../backend/src/ae_uptime_ce/static/css'
                    },
                    {
                        expand: true,
                        cwd: 'build/release/css',
                        src: ['front.css'],
                        dest: config.ae_webassets_location + '/' + packageInfo.name + '/css'
                    }
                ]
            },
            js: {
                files: [
                    // includes files within path and its sub-directories
                    {
                        expand: true,
                        cwd: 'build/release/js',
                        src: ['**'],
                        dest: '../backend/src/ae_uptime_ce/static/js'
                    },
                    {
                        expand: true,
                        cwd: 'build/release/js',
                        src: ['**'],
                        dest: config.ae_webassets_location + '/' + packageInfo.name + '/js'
                    }
                ]
            }
        },
        watch: {
            dev: {
                files: ['<%= concat.dev.src %>', 'src/**/*.html', '!build/*.js'],
                tasks: ['ngtemplates', 'concat:dev', 'concat:dist', 'copy:js']
            },
            css: {
                files: ['css/**/*.less', 'css/**/*.css'],
                tasks: ['less', 'copy:css']
            }
        },

        less: {
            dev: {
                files: {}
            }
        }

    };

    grunt.initConfig(grunt_conf_obj);

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-remove-logging');
    grunt.loadNpmTasks('grunt-angular-templates');
    grunt.loadNpmTasks('grunt-contrib-less');


    grunt.registerTask('styles', ['less']);
    grunt.registerTask('test', ['jshint', 'qunit']);

    grunt.registerTask('default', ['ngtemplates', 'concat:dev', 'removelogging', 'concat:dist', 'less', 'copy:js', 'copy:css']);

};
