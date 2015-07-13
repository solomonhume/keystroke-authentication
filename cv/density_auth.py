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

def determineThresh(uscores,iscores):
    cutoffs  = np.linspace((max(iscores)+.002),(min(uscores)-.002),100)
    FRR,IPR = np.array([]),np.array([])
    for i in range(len(cutoffs)):
            y = str(i)
            results['users'+y] = len(list(x for x in uscores if x <= cutoffs[i])) # users below threshold
            results['impostors'+y] = len(list(x for x in iscores if x <= cutoffs[i])) # impostors below threshold
            FRR = np.append(FRR,(1-float(results['users'+y])/float(len(uscores)))*100)
            IPR = np.append(IPR,float(results['impostors'+y])/float(len(iscores))*100)
    summed = FRR+IPR
    summin = np.argmin(summed)
    dif = abs(FRR-IPR)
    difmin = np.argmin(dif)
    return cutoffs[summin],cutoffs[difmin]

def evaluateThresh(uscores,iscores,sumThresh,difThresh):
    sumFRR = len(list(x for x in uscores if x >= sumThresh))/float(len(uscores)*100)
    difFRR = len(list(x for x in uscores if x >= difThresh))/float(len(uscores)*100)
    sumIPR = len(list(x for x in uscores if x <= sumThresh))/float(len(iscores)*100)
    sumIPR = len(list(x for x in uscores if x <= difThresh))/float(len(iscores)*100)
    return sumFRR,sumIPR,difFRR,difIPR
