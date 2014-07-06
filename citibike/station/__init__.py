#!/usr/bin/env python3

from bz2file import BZ2File
from citibike.cache import cache_filename
from citibike.reader import rides
from csv import DictReader
from functional import compose, partial
from functools import reduce
from gflags import FLAGS
from glob import glob
from itertools import chain
from json import load, dump, dumps
from os import environ
from os.path import basename, exists, join
from sys import argv, stderr


def get_stations():
    for ride in rides():
        yield ride['start station id'], {'longitude': ride['start station longitude'],
                                         'latitude': ride['start station latitude'],
                                         'name': ride['start station name'],
                                         'id': ride['start station id'],
                                         }
        yield ride['end station id'], {'longitude': ride['end station longitude'],
                                       'latitude': ride['end station latitude'],
                                       'name': ride['end station name'],
                                       'id': ride['end station id'],
                                       }


def unique_stations(subset=None):
    """Yield a dictionary for each unique station.
    
    Args:
      subset: An optional set of station_ids to search for.  The
              search will end once all of these will be identified.

    Yields:
      Dictionaries with station details. 
      {'longitude': ...,
       'latitude': ...,
       'name': ...,
       'id': ...}
    """
    subset = set(subset)
    stations = {}
    for station_id, station_data in get_stations():
        if subset is not None:
            if not subset:
                break
            if station_id not in subset:
                continue 
            subset.remove(station_id)
        previous_station_data = stations.get(station_id)
        if previous_station_data is not None:
            if previous_station_data == station_data:
                continue
            raise ValueError(
                "Inconsistent station data for station #%d: %r != %r" %
                (station_id, previous_station_data, station_data))
        else:
            stations[station_id] = station_data
    for station_data in stations.values():
        yield station_data


def run():
    for station_data in unique_stations():
        print(dumps(station_data))


def main(argv):
    try:
        argv = FLAGS(argv)[1:]
    except (gflags.FlagsError, KeyError, IndexError) as e:
        stderr.write("%s\nUsage: %s \n%s\n" % (
            e, basename(argv[0]), FLAGS))
        return 1
    return run()
