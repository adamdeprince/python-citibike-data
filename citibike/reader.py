#!/usr/bin/env python3

from csv import DictReader
from bz2file import BZ2File
from glob import glob
from itertools import chain
from sys import argv
from functional import compose, partial
from functools import reduce
import gflags
from glob import glob
from os.path import join
from os import environ
from citibike import cache

FLAGS = gflags.FLAGS


gflags.DEFINE_string('glob', '*.csv.bz2', 'Glob pattern to read from cache')

gflags.DEFINE_multistring('filter', [], 'Add filters')
gflags.DEFINE_multistring('exclude', [], 'Add exclusions')
gflags.DEFINE_boolean('details', True, 'If set to False, only the id# of the start and ending stations will be provided')

compose_mult = partial(reduce, compose) 

STATION_DETAILS = set(('start station longitude', 'start station latitude', 'end station longitude', 'end station latitude', 'end station name', 'start station name'))


def remove_station_details(record):
    """Removes station details from a record"""
    retval = {}
    for key, value in record.items():
        if key in STATION_DETAILS: continue
        retval[key] = value
    return retval


def rides(files=[]):
    def float(obj, _cache={}, float=__builtins__['float']):

        # Its important we have a memoized version of float to be
        # absolutely sure two strings with the same source compare
        # exactly.  This isn't defind in the global scope for a few
        # reasons - for one, we only really care about comparisons
        # within a single pass for the benefit of
        # citibike.station:unique_stations's ability to dedup
        # statiions and not accidentally raise a ValueError.  So
        # there's no point to corrupting the global scope, interning
        # extra floats or keeping any of the interned relationships
        # after rides ends.

        if obj in _cache: 
            return _cache[obj]

        f = float(obj)
        _cache[obj] = f
        return f

    
    files = files or sorted(glob(join(FLAGS.cache, '*.csv.bz2')))
    if not files: return
    for ride in chain(*(DictReader(BZ2File(f)) for f in files)):
        ride['start station id'] = int(ride['start station id'])
        ride['end station id'] = int(ride['end station id'])
        ride['start station latitude'] = float(ride['start station latitude'])
        ride['start station longitude'] = float(ride['start station longitude'])
        ride['end station latitude'] = float(ride['end station latitude'])
        ride['end station longitude'] = float(ride['end station longitude'])
        yield ride

def run():
    qs = Query(rides())
    qs = qs.filter(**dict(f.split('=') for f in FLAGS.filter))
    qs = qs.exclude(**dict(f.split('=') for f in FLAGS.exclude))
            
    for ride in qs:
        if not FLAGS.details:
            ride = ride(remove_station_details(ride))
        try:
            print(ride)
        except IOError:
            break


class Query:
    def __init__(self, seq):
        self.seq = seq
        self.filter_func = []

    def filter(self, **kwargs):
        q = Query(self)
        q.__set_filter(kwargs)
        return q

    def exclude(self, **kwargs):
        q = Query(self)
        q.__set_exclude(kwargs)
        return q

    def __set_filter(self, kwargs):
        for key, value in kwargs.items():
            def a_filter(seq, key=key, value=value):
                if True:
                    for item in seq:
                        if item[key] == value:
                            yield item
            self.filter_func.append(a_filter)
    
    def __set_exclude(self, kwargs):
        for key, value in kwargs.items():
            def a_filter(seq, key=key, value=value):
                if True:
                    for item in seq:
                        if item[key] != value:
                            yield item
            self.filter_func.append(a_filter)
    
    def __iter__(self):
        if self.filter_func:
            seq = self.seq
            for f in self.filter_func:
                seq = f(seq)
            for i in seq:
                yield i
        else:
            for x in self.seq:
                yield x
        
        


def main(argv):
    try:
        argv = FLAGS(argv)[1:]
    except (gflags.FlagsError, KeyError, IndexError), e:
        sys.stderr.write("%s\nUsage: %s \n%s\n" % (
                e, os.path.basename(sys.argv[0]), FLAGS))
        return 1
    run()
