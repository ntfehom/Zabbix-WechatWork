#!/usr/bin/env python3
# coding:utf-8
from setuptools import find_packages, setup

setup(
    name='Zabbix-WechatWork',
    version='1.0.4',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask==1.1.2',
        'pycrypto==2.6.1',
    ],
)