Citibike data for python
========================

The easiest way for python programmers to download and work with NYC's
public citibike dataset.  The citibike module provides both a command
line interface and convenient API for filtering and streaming citibike
data.


Installation
============

Lets get started by installing the citibike python module and
downloading the citibike dataset.    The download will take a few minutes.

Before doing this make sure you have enough space on your hardrive in
your home directory.  As of early May 2014 the citibike data set,
recompressed with bzip2, takes 80Mb.

````bash
pip install citibike
citibike_download_originals # Caches data in ~/.citibike 
citibike_stations > /dev/null # Build the station list cache
````

Citibike publishes data a month at a time; to update your dataset
simply run these two commands monthly.  citibike_download_originals
will only download and recompress new data files.

````bash
citibike_download_originals 
citibike_stations > /dev/null
````

CHANGES
=======

0.0.4 - citibike_dump generates proper json; add citibike_station_mapper command

0.0.3 - stationid, tripduration, bikeid, gender and birth year are
treated as integers instead of strings.







