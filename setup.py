# -*- coding: utf-8 -*-
"""
This module contains the tool of jarn.kommuner
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n')


setup(name='jarn.kommuner',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['jarn', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.testing'
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
