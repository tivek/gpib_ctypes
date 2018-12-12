#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(tivek): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='gpib_ctypes',
    version='0.3.0',
    description="GPIB interface for Python implemented using ctypes, API-compatible with linux-gpib.",
    long_description=readme + '\n\n' + history,
    author="Tomislav Ivek",
    author_email='tomislav.ivek@gmail.com',
    url='https://github.com/tivek/gpib_ctypes',
    packages=find_packages(exclude=['tests', 'test']),
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v2",
    zip_safe=False,
    keywords='gpib_ctypes',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
