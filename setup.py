# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Copyright Yeepay.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='smw-light',
    version='1.0.0',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='SMW Team',
    author_email='.com',
    url='https://github.com/',
    license='Apache License',
    platforms=["all"],
    packages=find_packages(exclude=["test", "test_*"]),
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'pandas>=1.1.4',
        'matplotlib>=3.141.0',
        'mplfinance>=4.9.0',
    ],
    # python_requires='~=2.7,~=3.2',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-html',
    ],
)
