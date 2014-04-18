#!/usr/bin/env python
"""
py-citibike
"""

from setuptools import setup


setup(
    name='citibike',
    version='0.0.0',
    author='Adam DePrince',
    author_email='deprince@googlealumni.com',
    description='',
    long_description=__doc__,
    py_modules = [
        'citibike/__init__',
        'citibike/reader',
        'citibike/download',
        'citibike/station',
        ],
    packages = ['citibike'],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        # 'scripts/citibike_to_postgresql'
        'scripts/citibike_download_originals', # Downloads and unpacks original citibike data
        'scripts/citibike_dump', # Downloads and unpacks original citibike data
        'scripts/citibike_stations', #Dumps station data and manages station data cache
        ],
    url = 'https://github.com/adamdeprince/python-citibike-data',
    install_requires = [
        'bz2file',
        'boto',
        'functional',
        'python-gflags',
        'requests',
        'progressbar',
        ]
)

