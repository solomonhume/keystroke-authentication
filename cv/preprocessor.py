import collections as coll
import os

DATA_DIR = './combine'
FILE_LS = next(os.walk(DATA_DIR))[-1]


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
        if ng_t[0] in d: d[ng_t[0]].append(ng_t[1])
        else: d[ng_t[0]] = [ng_t[1]]
    return d


def split_samples(data_dict, sample_size=1000):
    '''
    takes dict (user str -> [(ngraph, latency)])
    optional args
    sample size, defaults to 1000 (keystrokes)
    returns dict (user str -> [(ngraph -> [latency])])
    '''
    return {k:map(ngraph_ls2dict,chunkify(v,sample_size)) for k,v in data_dict.items()}


if __name__=='__main__':
    d = split_samples(load_data())
    print len(d)
    #print len(d['1227981'])
    #print d['1227981'][0]['TH'][:10]
