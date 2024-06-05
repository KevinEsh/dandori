#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from version import __version__

requirements = [
    # TODO: put package requirements here
    "gstorm == 0.6.0",
    "redis == 3.5.3",
    "ortools == 7.8.7959",
    "numpy == 1.19.2",
    "networkx == 2.5",
    "matplotlib == 3.3.3",
    "pandas == 1.2.3",
]

setup_requirements = [
    # TODO: put setup requirements (distutils extensions, etc.) here
    'pylint == 2.6.0',
    'sphinx == 3.1',
    'sphinx-rtd-theme == 0.5.0',
    'autopep8 == 1.5.4',
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest == 6.1.2',
    'pytest-cov == 2.10.1',
]

desc = "Smart Scheduler for manufactoring industries"
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dandori',
    version=__version__,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="KevinEsh",
    author_email="godspeed.ai@outlook.com",
    url='https://github.com/KevinEsh/dandori',
    packages=find_packages(include=['scheduler']),
    entry_points={},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords=['scheduler', 'manufactory', 'python'],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
