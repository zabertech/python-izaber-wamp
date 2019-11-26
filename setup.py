#!/usr/bin/python

from setuptools import setup

setup(name='izaber_wamp',
      version='2.20191126',
      description='Base load point for iZaber WAMP code',
      url = 'https://github.com/zabertech/python-izaber-wamp',
      download_url = 'https://github.com/zabertech/python-izaber-wamp/archive/2.20191126.tar.gz',
      author='Aki Mimoto',
      author_email='aki+izaber@zaber.com',
      license='MIT',
      packages=['izaber_wamp'],
      scripts=[],
      install_requires=[
          'izaber',
          'swampyer',
      ],
      dependency_links=[],
      zip_safe=False)

