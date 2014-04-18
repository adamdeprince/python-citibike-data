#!/usr/bin/env python3

from bz2file import BZ2File
from citibike.cache import cache_filename
from citibike.reader import rides
from csv import DictReader
from functional import compose, partial
from functools import reduce
from glob import glob
from glob import glob
from itertools import chain
from json import dumps, load 
from os import environ
from os.path import join, exists, basename
from sys import argv, stderr


import gflags
FLAGS = gflags.FLAGS


gflags.DEFINE_boolean('rebuild_station_cache', False, 'This module will by default try to read from the station cache and only compute the station list of that fails.  Setting this to true will ignore the caceh, recompute this data and write a new cache file.  This is something you should run after successfully downloading new data sets with citibike_download') 

def stations():
    for ride in rides():
        yield ride['start station id'], {'longitude':ride['start station longitude'],
                                         'latitude':ride['start station latitude'],
                                         'name':ride['start station name'],
                                         'id':ride['start station id'],
                                     }
        yield ride['end station id'], {'longitude':ride['end station longitude'],
                                        'latitude':ride['end station latitude'],
                                        'name':ride['end station name'],
                                        'id':ride['end station id'],
                                    }
                                        

def unique_stations():
    if not FLAGS.rebuild_station_cache and exists(cache_filename('unique_stations')):
        for _ in load(open(cache_fileanme('unique_stations'))):
            yield _
        
    cached_stations = {}
    for station_id, station_data in stations():
        previous_station_data = cached_stations.get(station_id)
        if previous_station_data is not None:
            if previous_station_data == station_data:
                continue
            raise ValueError("Inconsistent station data for station #%d: %r != %r" % (station_id, previous_station_data, station_data))
        else:
            cached_stations[station_id] = station_data
    if FLAGS.rebuild_station_cache:
        dump(cached_stations.values(), open(cahce_filename('unique_stations'), 'w+'))
    for station_data in cached_stations.values():
        yield station_data 

def run():
    for station_data in unique_stations():
        print(dumps(station_data))


def main(argv):
    try:
        argv = FLAGS(argv)[1:]
    except (gflags.FlagsError, KeyError, IndexError), e:
        stderr.write("%s\nUsage: %s \n%s\n" % (
                e, basename(argv[0]), FLAGS))
        return 1
    return run()
