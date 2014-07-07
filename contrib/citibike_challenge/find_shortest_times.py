#!/usr/bin/env python

from json import loads
from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

class FindShortestTimes(MRJob):
    def mapper(self, _, line):
        line = loads(line)
        key = (line['start station id'], line['end station id'])
        if key[0] != key[1]:
            yield key, int(line['tripduration'])

    def reducer(self, key, values):
        start_station_id, stop_station_id = key
        yield key, {'start station id': start_station_id,
                    'end station id': end_station_id,
                    'tripduration': min(values)}
        
    OUTPUT_PROTOCOL =  JSONValueProtocol

if __name__ == '__main__':
    FindShortestTimes.run()
