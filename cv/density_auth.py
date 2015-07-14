import numpy as np
import statsmodels.api as sm
from scipy import stats

def kdensity(data):
    """
    calculate the kernel density for a ngraph -> [latencies]
    """
    temp = np.array(data)
    if len(temp)>2:
        kde = sm.nonparametric.KDEUnivariate(temp.astype(float))
        kde.fit(bw=nrd0(temp))
        d = kde.evaluate(range(501))
        return d
    else:
        return 0

def nrd0(x):
    """
    caluclate bandwith of kernel using silverman's rule of thumb(same as bw.nrd0 in R)
    """
    hi = np.std(x)
    IQR = np.subtract.reduce(np.percentile(x, [75,25]))
    attempt = 0
    lo = min(hi,IQR/1.34)
    while lo == 0:
        if attempt == 0:
            lo =  hi
            attempt = 1
        elif attempt == 1:
            lo = abs(x[1])
            attempt = 2
        else:
            lo = 1
    return 0.9 * lo * len(x)**(-0.2)

def density_scoring(train,val):
    '''
    takes 2 dictionaries {users -> [{ngraphs -> [latency]}]}
    returns a dictionary {users -> [(avg density difference, 1|0 (genuine/impostor))]}
    '''
    d_dict = {u:[] for u in train.keys()}
    # train,val has type (user, [{ngraphs -> [latency]}])
    for user_samples in train.iteritems():
        current_user = user_samples[0]
        for samp in user_samples[1]:
            for u in d_dict.keys():
                d_dict[u].append(
                    ( difference(train[u],val[u]),
                      int(u==current_user) )
                )
    return d_dict

def difference(prof1,prof2):
    count = 0 # count of unique diagraphs shared between the prof and the reference prof
    score = 0 # a sum of differences between density plot for each test
    for i in prof1: # for all diagraphs in the profile
        if i in prof2: # if the diagraph exists in the reference profile
            sumval =  np.sum(np.absolute(prof1[i]-prof2[i]))
            count += 1 # increment count
            score += sumval #add the difference between the two densities to the score
    if count != 0:
        return score/float(count)
