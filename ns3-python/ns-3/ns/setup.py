#!/usr/bin/env python3

import os
from sys import platform
from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build
from subprocess import call
from multiprocessing import cpu_count

NS3_BUILD_PATH = '/ns-3-build'
NS3_VERSION = os.environ['NS3_VERSION']

class NS3Build(build):
  def run(self):
    super().run()
    self.copy_tree(f'{NS3_BUILD_PATH}/usr/local/lib/python3.9/site-packages/ns', self.build_lib + '/ns')
    self.copy_tree(f'{NS3_BUILD_PATH}/usr/local/lib', self.build_lib + '/ns/_/lib')
    self.copy_tree(f'{NS3_BUILD_PATH}/usr/local/bin', self.build_lib + '/ns/_/bin')

class NS3Install(install):
  def run(self):
    super().run()
    self.copy_tree(self.build_lib, self.install_lib)

def read(filename):
  with open(filename, 'r') as file:
    return file.read()

setup(
  name='ns',
  version=NS3_VERSION,
  description='a discrete-event network simulator for internet systems',
  license='GPLv2',
  url='https://www.nsnam.org',
  classifiers=[
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: Unix',
    'Programming Language :: C++',
  ],
  cmdclass={
    'build': NS3Build,
    'install': NS3Install,
  },
)
