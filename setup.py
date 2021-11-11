# -*- coding: utf-8 -*-

from setuptools import setup

from art import __version__

tests_require = ['pytest', 'pytest-cov', 'pytest-mock', 'wheel']
setup(
    name='art',
    description='Artifact manager',
    author='Valohai',
    author_email='hait@valohai.com',
    license='MIT',
    version=__version__,
    packages=['art'],
    entry_points={'console_scripts': ['art=art.command:run_command']},
    install_requires=['boto3', 'pyyaml'],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
