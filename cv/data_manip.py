import collections as coll

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


def process_latencies(lat_dict, proc):
    '''
    Takes a latency dictionary (user str -> (ngraph -> [latencies]))
    and a function operating on lists of latencies
    returns a dictionary (user str -> (ngraph -> processed_latencies))
    '''
    p_lat = {}
    for u in lat_dict.keys():
        p_lat[u] = coll.defaultdict(lambda x: (-1., -1., -1.))
        for ng in lat_dict[u].keys():
            p_lat[u][ng] = proc(lat_dict[u][ng])
    return p_lat
