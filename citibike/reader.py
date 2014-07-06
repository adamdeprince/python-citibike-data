#!/usr/bin/env python3

from datetime import date
from csv import DictReader
from bz2file import BZ2File
from glob import glob
from itertools import chain
from sys import argv
from functional import compose, partial
from functools import reduce
import gflags
from glob import glob
from os.path import join, basename
from os import environ
from citibike import cache
from json import dumps
import sys
import os
FLAGS = gflags.FLAGS


gflags.DEFINE_string('glob', '*.csv.bz2', 'Glob pattern to read from cache')
gflags.DEFINE_string('start', None, 'Start date formatted as year/month/day')
gflags.DEFINE_string('end', None, 'End date (inclusive) formatted as year/month/day')
gflags.DEFINE_multistring('filter', [], 'Add filters')
gflags.DEFINE_multistring('exclude', [], 'Add exclusions')
gflags.DEFINE_boolean(
    'details',
    True,
    'If set to False, only the id# of the start and ending stations will be provided')

compose_mult = partial(reduce, compose)

STATION_DETAILS = set(
    ('start station longitude',
     'start station latitude',
     'end station longitude',
     'end station latitude',
     'end station name',
     'start station name'))

def int_or_none(value):
    try:
        return int(value)
    except:
        return None

def parse_date(d):
    if d is None:
        return None
    y, m, d = map(int, d.split('-'))
    return date(y, m, d)

def validate_date(d):
    try:
        parse_date(d)
        return True
    except:
        return False


gflags.RegisterValidator('start',
                        validate_date,
                        message='Incorrect date format',
                        flag_values=FLAGS)

gflags.RegisterValidator('end',
                        validate_date,
                        message='Incorrect date format',
                        flag_values=FLAGS)


def remove_station_details(record):
    """Removes station details from a record"""
    retval = {}
    for key, value in record.items():
        if key in STATION_DETAILS:
            continue
        retval[key] = value
    return retval


class DateChecker():
    last_str = None
    last_date = None
    def __init__(self, start, stop):
        self.start, self.stop = map(parse_date, (start, stop))

        if None not in (self.start, self.stop):
            self.start, self.stop = sorted((self.start, self.stop))

        self.start_file = (self.start.year, self.start.month) if self.start else None
        self.stop_file = (self.stop.year, self.stop.month) if self.stop else None
        
    @staticmethod
    def parse_filename(fn):
        fn = basename(fn)
        fn = fn.split()[0].split('-')
        return tuple(map(int, fn))

    @classmethod
    def parse_date_from_timestamp(cls, d):
        d = d.split()[0]
        if cls.last_str == d.split()[0]:
            return cls.last_date
        cls.last_str = d
        d = date(*map(int, d.split('-')))
        cls.last_date = d
        return d

    def valid_row(self, row):
        date = self.parse_date_from_timestamp(row['starttime'])
        if self.stop and date > self.stop:
            raise StopIteration
        return self.start is None or date >= self.start
        

    def valid_file(self, fn):
        fn = self.parse_filename(fn)
        year, month = fn
        if self.stop_file is not None:
            if (year,month) > self.stop_file:
                return False
        if self.start_file is not None:
            if (year, month) < self.stop_file:
                return False
        return True




def rides(files=[]):
    def float(obj, _cache={}, float=__builtins__['float']):

        date_checker = DateChecker(FLAGS.start, FLAGS.end)
        start, end = map(parse_date, (FLAGS.start, FLAGS.end))
        if None not in (start,end):
            start,end = sorted((start, end))

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

    date_checker = DateChecker(FLAGS.start, FLAGS.end)
    files = files or sorted(glob(join(FLAGS.cache, '*.csv.bz2')))
    files = filter(date_checker.valid_file, files)
    if not files:
        return
    for ride in chain(*(DictReader(BZ2File(f)) for f in files)):
        if not date_checker.valid_row(ride): continue 
        ride['start station id'] = int_or_none(ride['start station id'])
        ride['end station id'] = int_or_none(ride['end station id'])
        ride['tripduration'] = int_or_none(ride['tripduration'])
        ride['bikeid'] = int_or_none(ride['bikeid'])
        ride['gender'] = int_or_none(ride['gender'])
        ride['birth year'] = int_or_none(ride['birth year'])
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
            print(dumps(ride))
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
    except (gflags.FlagsError, KeyError, IndexError) as e:
        sys.stderr.write("%s\nUsage: %s \n%s\n" % (
            e, os.path.basename(sys.argv[0]), FLAGS))
        return 1
    try:
        run()
    except IOError:
        return 0
    finally:
        sys.stderr.close()
        sys.stdout.close()
