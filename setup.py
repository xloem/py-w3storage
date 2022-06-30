# SPDX-License-Identifier: GPL-2.0-or-later

from setuptools import setup, find_packages

setup(
        name='w3storage',
        version='0.0.1',
        description='A Python client for https://web3.storage',
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        url='https://github.com/xloem/py-w3storage',
        packages=find_packages(),
        install_requires=[
            'requests',
        ],
        license='GPLv2+',
        classifiers=[
            'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
        ]
)
