#!/usr/bin/python

from setuptools import setup

setup(name='izaber_wamp',
      version='2.00',
      description='Base load point for iZaber WAMP code',
      url='',
      author='Aki Mimoto',
      author_email='aki+izaber@zaber.com',
      license='MIT',
      packages=['izaber_wamp'],
      scripts=[],
      install_requires=[
          'izaber',
          'websocket-client',
          'six',
      ],
      dependency_links=[
          'git+https://gitlab.izaber.com/systems/izaber.git#egg=izaber-1.05'
      ],
      zip_safe=False)

