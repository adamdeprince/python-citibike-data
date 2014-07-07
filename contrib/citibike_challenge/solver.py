from json import loads
from tsp_solver.greedy import solve_tsp
import sys
from json import dumps

# Load shortest_times.txt and put it into the times variable.
times = {}
for line in open("shortest_times.txt"):
    line = loads(line)
    times[line['start station id'], line['end station id']] = line['tripduration']

# If there's a route from a to b, and not one from b to a, assume it takes the same amount of time. 
update = {}
for start, end in times:
    if (end, start)  not in times:
        update[(end, start)] = times[(start, end)]
    elif times[(end, start)] > times[(start, end)]:
        update[(end, start)] = times[(start, end)]
times.update(update)
del(update)

# According to Google maps, the furthuest two points in the citibike system are 51 minutes apart. 
longest_possiable_trip = 51 * 60 
for start_end, duration in times.items():
    if duration > longest_possiable_trip:
        times[start_end] = 51 * 60

# Figure out a list of all our stations.

stations = set()
for start, end in times:
    stations.add(start)
    stations.add(end)

stations = sorted(stations)

# We can use stations to compute the station for an index, but getting
# the index of a station requires we have a dictionary to look it up
# in.

station_2_index = {}
for index, station in enumerate(stations):
    station_2_index[station] = index


# Build our matrix.  
matrix = []
for _ in range(len(stations)):
    matrix.append([longest_possiable_trip] * len(stations))

for ((start, end), time) in times.items():
    start = station_2_index[start]
    end = station_2_index[end]
    matrix[start][end] = time

def pairs(i):
    i = iter(i)
    last_item = i.next()
    for item in i:
        yield last_item, item
        last_item = item

path = solve_tsp(matrix, optim_steps=10000)
path = [stations[index] for index in path]
print >>sys.stderr, "Total time:", sum(times.get(pair, longest_possiable_trip) for pair in pairs(path))
print " ".join(map(str, path))
    

    
