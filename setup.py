#!/usr/bin/python

from setuptools import setup

import izaber

setup(name='izaber_wamp',
      version='1.00',
      description='Base load point for iZaber WAMP code',
      url='',
      author='Aki Mimoto',
      author_email='aki+izaber@zaber.com',
      license='MIT',
      packages=['izaber_wamp'],
      scripts=[],
      install_requires=[
          'izaber'
      ],
      zip_safe=False)

