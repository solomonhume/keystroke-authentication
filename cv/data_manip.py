import collections as coll
import itertools
from time import strftime

import scipy.stats as stats


def get_ngraphs(training_data):
    '''
    takes a list of latency dictionaries, returns 
    set of ngraphs for a user.
    '''
    result = set()
    for d in training_data:
        result |= set(d.keys())
    return result


def to_lat_dict(training_data):
    '''
    takes {username -> [latency dictionary]}
    where latency dictionaries represent samples of 1k ngraphs
      organized into {ngraph -> [integers]}
    returns {username -> latency dictionary}
    i.e. merges all latency dictionaries.
    '''
    lat_dict = {}
    for u in training_data.keys():
        lat_dict[u] = {ng:sum((training_data[u][i][ng] 
                               for i in range(len(training_data[u]))),
                              [])
                       for ng in get_ngraphs(training_data[u])}
    return lat_dict


def process_latencies(lat_dict, proc, default):
    '''
    Takes a latency dictionary (user str -> (ngraph -> [latencies]))
    and a function operating on lists of latencies
    and a function returning a default value
    returns a dictionary (user str -> (ngraph -> processed_latencies))
    where (ngraph-> processed_latencies) is a default dict using the 
    specified default function.
    '''
    p_lat = {}
    for u in lat_dict.keys():
        p_lat[u] = coll.defaultdict(default)
        for ng in lat_dict[u].keys():
            p_lat[u][ng] = proc(lat_dict[u][ng])
    return p_lat


def partition_data(u, samples, p):
    '''
    takes a username and list of dictionaries [(n-graph -> [latencies])]
    generates partitions l1, l2 [(n-graph -> [latencies])]
    so that len(l2) = p
    and returns u, l1, l2
    '''
    sample_numbers = xrange(len(samples))
    for leftout_ind in itertools.combinations(sample_numbers,p):
        val_samples = [ samples[i]
                        for i in list(leftout_ind) ]
        train_samples = [ samples[i]
                          for i in sample_numbers
                          if not i in list(leftout_ind) ]
        yield u, train_samples, val_samples

def timestamp(msg):
    print strftime('%H:%M:%S'), '-', msg
