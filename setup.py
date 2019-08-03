#!/usr/bin/python
#

from setuptools import setup
import os


def is_package(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, "__init__.py"))


def find_packages(path, base=""):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


packages = find_packages(".")
package_names = packages.keys()

packages_required = ["webthing"]

setup(
    name="tsl2561-webthing",
    version="1.0.0",
    description="tsl2561 lux sensor",
    author="ptaylour",
    packages=package_names,
    package_dir=packages,
    scripts=["bin/tsl2561-webthing"],
    data_files=[
        ("/lib/systemd/system", ["lib/systemd/system/tsl2561-webthing.service"])
    ],
    install_requires=packages_required,
    long_description="A webthing that reports the current lux read from a sensor",
)
