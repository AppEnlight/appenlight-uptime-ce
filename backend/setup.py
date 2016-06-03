"""A setuptools based setup module.
"""
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

REQUIREMENTS = open(path.join(here, 'requirements.txt')).readlines()

compiled = re.compile('([^=><]*).*')


def parse_req(req):
    return compiled.search(req).group(1).strip()

requires = [_f for _f in map(parse_req, REQUIREMENTS) if _f]

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ae_uptime_ce',
    version='1.0',
    description='Appenlight Uptime Monitoring CE',
    long_description=long_description,
    url='https://',
    author='RhodeCode',
    author_email='support@rhodecode.com',
    license='commercial',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Monitoring',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='appenlight uptime monitoring',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'appenlight-uptime-monitor = ae_uptime_ce.scripts.uptime_monitor:main',
        ],
        'appenlight.plugins':[
            'ae_uptime_ce = ae_uptime_ce'
        ]
    },
)
