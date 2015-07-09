import numpy as np
import statsmodels.api as sm
from scipy import stats

def density(data):
    """
    calculate the kernel density for a ngraph -> [latencies]
    """
    d = {}
    for u in data:
        for dgraph,laten in data[u]:
            if len(laten)>2:
                kde = sm.nonparametric.KDEUnivariate(laten)
                kde.fit(bw=nrd0(laten))
                d[u][dgraph] = kde.evaluate(range(501))
    return d

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

def difference(prof1,prof2):
    """
    take the density differences of two digraphs, add them together for all
    digraphs for a given user, divide by number of shared diagraphs
    """
    count,score = 0
    for i in prof1:
        if i in prof2:
            count += 1
            score += np.sum(np.absolute(prof1[i]-prof2[i]))
    if count!= 0:
        return score/float(count)
