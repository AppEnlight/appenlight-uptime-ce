"""A setuptools based setup module.
"""
import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

REQUIREMENTS = open(path.join(here, "requirements.txt")).readlines()

compiled = re.compile("([^=><]*).*")


def parse_req(req):
    return compiled.search(req).group(1).strip()


requires = [_f for _f in map(parse_req, REQUIREMENTS) if _f]

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


def _get_meta_var(name, data, callback_handler=None):
    import re

    matches = re.compile(r"(?:%s)\s*=\s*(.*)" % name).search(data)
    if matches:
        if not callable(callback_handler):
            callback_handler = lambda v: v

        return callback_handler(eval(matches.groups()[0]))


with open(os.path.join(here, "src", "ae_uptime_ce", "__init__.py"), "r") as _meta:
    _metadata = _meta.read()

with open(os.path.join(here, "VERSION"), "r") as _meta_version:
    __version__ = _meta_version.read().strip()

__license__ = _get_meta_var("__license__", _metadata)
__author__ = _get_meta_var("__author__", _metadata)
__url__ = _get_meta_var("__url__", _metadata)

setup(
    name="ae_uptime_ce",
    version=__version__,
    description="Appenlight Uptime Monitoring CE",
    long_description=long_description,
    url=__url__,
    author=__author__,
    author_email="support@rhodecode.com",
    license=__license__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Monitoring",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    keywords="appenlight uptime monitoring",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=requires,
    entry_points={
        "console_scripts": [
            "appenlight-uptime-monitor = ae_uptime_ce.scripts.uptime_monitor:main"
        ],
        "appenlight.plugins": ["ae_uptime_ce = ae_uptime_ce"],
    },
)
