import collections as coll
import itertools
import os

import scipy.misc as misc

from data_manip import partition_data

DATA_DIR = './combine'
FILE_LS = next(os.walk(DATA_DIR))[-1]

OUTER_GT = 100
INNER_GT = 100

def load_data(ng_len=2, lat_lb=20, lat_ub=500):
    '''
    optional args
    ngraph length, defaults to 2
    lower bound on latency, defaults to 20
    upper bound on latency, defaults to 500

    returns dict (user str -> [(ngraph, latency)])
    '''
    data_dict = {}
    d = {}

    for f in FILE_LS:
        data = file(DATA_DIR+'/'+f).read()
        pairs = [x.rsplit(':',1)
            for x in
            data.replace('\n','\t').split('\t')
            ]
        pairs = [(x[0], int(x[1])) for x in pairs if len(x) == 2]
        ngraphs = []
        for i in range(len(pairs)-ng_len):
            ng_t = (''.join([x[0] for x in pairs[i:i+ng_len]]),
                        pairs[i+ng_len][1] - pairs[i][1])
            if lat_lb <= ng_t[1] <= lat_ub: ngraphs.append(ng_t)
        k = f[:-4] #the file name without extension (e.g. ".txt")
        d[k] = ngraphs
    return d


def chunkify(ls, sz):
    '''
    takes list of elements
    returns list of lists of size sz, drops last if size less than sz
    '''
    return [ls[x:x+sz] for x in range(0, len(ls), sz) if len(ls[x:x+sz]) == sz]


def ngraph_ls2dict(ls):
    '''
    takes [(ngraph, latency)]
    returns dict (ngraph -> [latency])
    '''
    d = coll.defaultdict(list)
    for ng_t in ls:
        if ng_t[0] in d: d[ng_t[0]].append(float(ng_t[1]))
        else: d[ng_t[0]] = [float(ng_t[1])]
    return d


def split_samples(data_dict, sample_size=1000):
    '''
    takes dict (user str -> [(ngraph, latency)])
    optional args
    sample size, defaults to 1000 (keystrokes)
    returns dict (user str -> [(ngraph -> [latency])])
    '''
    return {k:map(ngraph_ls2dict,chunkify(v,sample_size)) for k,v in data_dict.items()}


def filter_users_val(sample_dict):
    '''
    takes dict (user str -> [(ngraph -> [latency])])
    returns a dict of the same type so that
    only users who can supply the necessary amount of
    inner/outer genuine validation tests are kept.
    also returns dict containing values of p for each user
    (i.e. leave-p-out per outer validation split)
    and dict containing values of k for each users
    (i.e. leave-k-out per inner validation split)

    could reduce N loop to ceil(N/2), cache comb approximations
    '''
    pk_combs_d = {}
    for u in sample_dict.keys():
        N = len(sample_dict[u])
        # find min i so that i*C(N,i) >= OUTER_GT
        for i in range(1,N):
            if i*misc.comb(N,i) >= OUTER_GT:
                pk_combs_d[u] = i
                break
        else:
            continue

        p = pk_combs_d[u]
        # find min i so that i*C(N-p,i) >= INNER_GT
        for i in range(1,N-p):
            if i*misc.comb(N-p, i) >= INNER_GT:
                pk_combs_d[u] = (p, i, p*misc.comb(N,p), i*misc.comb(N-p,i))
                break
        else:
            del pk_combs_d[u]
    for u in [x for x in sample_dict.keys() if not x in pk_combs_d.keys()]:
        del sample_dict[u]
    assert set(sample_dict.keys()) == set(pk_combs_d.keys())
    return sample_dict, pk_combs_d

if __name__=='__main__':
    d = split_samples(load_data())
    f, pkd = filter_users_val(d)
    print len(d.keys())
    print 'user,', 'p,', 'k,', 'outer combinations,', 'inner combinations,'
    for k,x in pkd.items(): 
        print k, ',', x[0], ',', x[1], ',', int(x[2]/x[0]), ',', int(x[3]/x[1])
        
    print ((pkd['1227981'][2]/pkd['1227981'][0])*
           (pkd['1227981'][3]/pkd['1227981'][1])*
           (pkd['9999999'][2]/pkd['9999999'][0])*
           (pkd['9999999'][3]/pkd['9999999'][1])
    )
    for u in f.keys():
        if not u in ['1227981', '9999999']:
            del f[u]
    data = f
    p = {u:int(pkd[u][0]) for u in ['1227981', '9999999']}
    k = {u:int(pkd[u][1]) for u in ['1227981', '9999999']}
    i1 = itertools.product(
        *[partition_data(u, data[u], p[u])
          for u in ['1227981', '9999999']]
    )
    lli1 = len(list(i1))
    i1 = itertools.product(
        *[partition_data(u, data[u], p[u])
          for u in ['1227981', '9999999']]
    )

    for i in i1:
        train = {x[0]:x[1] for x in list(i)}

        i2 = itertools.product(
            *[partition_data(u, train[u], k[u])
              for u in ['1227981', '9999999']]
        )
        lli2 = len(list(i2))
        break
    
    print lli1, lli2
    print lli1*lli2

