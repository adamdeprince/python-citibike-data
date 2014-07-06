from citibike.station import unique_stations
from itertools import imap
from gflags import FLAGS
from sys import stdin
from geojson import LineString, Point, GeometryCollection, dumps


def station_ids_to_stations(station_ids):    
    stations = unique_stations(subset=station_ids)
    stations = dict((station['id'], station) for station in stations)
    
    for station_id in station_ids:
        yield stations.get(station_id)

def stations_to_geojson(stations):
    stations = list(stations)
    items = [
        LineString([(station['longitude'], station['latitude']) for station in stations])
        ]
    for station in stations:
        items.append(Point(coordinates=(
            station['longitude'],
            station['latitude'],
        ),
                           properties={'name':station['name'],
                                       'id': station['id']}))
    return GeometryCollection(items)


def run(station_id_stream):
    station_ids = filter(None, station_id_stream.read().split())
    station_ids = map(int, station_ids)
    stations = station_ids_to_stations(station_ids)
    print dumps(stations_to_geojson(stations))


def main(argv): 
    try:
        argv = FLAGS(argv)[1:]
        if len(argv) not in (0, 1):
            raise ValueError("Too many parameters - only accepts a single optional parameter")
    except (gflags.FlagsError, KeyError, IndexError, ValueError) as e:
        stderr.write("%s\nUsage: %s [infile.txt]\n%s\nAccepts a list of station_ids" % (
            e, basename(argv[0]), FLAGS))
        return 1
    if argv:
        station_id_stream = open(argv[0])
    else:
        station_id_stream = stdin
    return run(station_id_stream)
