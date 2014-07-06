#!/usr/bin/env python
"""
py-citibike
"""

from setuptools import setup

setup(
    name='citibike',
    version='0.0.4',
    author='Adam DePrince',
    author_email='deprince@googlealumni.com',
    description='',
    long_description=__doc__,
    py_modules=[
        'citibike/__init__',
        'citibike/reader',
        'citibike/download',
        'citibike/station/__init__',
        'citibike/station/mapper',
    ],
    packages=['citibike'],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
    ],
    scripts=[
        # 'scripts/citibike_to_postgresql'
        'scripts/citibike_download_originals',
        # Downloads and unpacks original citibike data
        'scripts/citibike_dump',
        # Downloads and unpacks original citibike data
        'scripts/citibike_stations',
        # Dumps station data and manages station data cache
        'scripts/citibike_station_mapper'
    ],
    url='https://github.com/adamdeprince/python-citibike-data',
    install_requires=[
        'bz2file',
        'functional',
        'geojson',
        'python-gflags',
        'requests',
        'progressbar',
    ]
)
