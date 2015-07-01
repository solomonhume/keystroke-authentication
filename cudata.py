import numpy as np
import os
import statsmodels.api as sm
import sys
import csv
import itertools
from scipy import stats
from statsmodels.distributions.mixture_rvs import mixture_rvs
from time import strftime


def chunk(list1, num):  # function to split a list into roughly equal parts
    avg = len(list1) / float(num)
    out = []
    last = 0.0
    while last < len(list1):
        out.append(list1[int(last):int(last + avg)])
        last += avg
    if len(out)>num:
        del out[-1]
    return out

def div(l, n):
    n = max(1, n)
    last = [l[i:i + n] for i in range(0, len(l), n)]
    return last

def orgDiagraph(dict1, dia ,time): # function to orgainze diagraphs into dictionary
    if len(dia)>1:
        if dia[0]+dia[1] in dict1: # index dictionary at diagraph, check if it exists
            dict1[dia[0]+dia[1]] = np.append(dict1[dia[0]+dia[1]],time) # add time value to list
        else: # if the the index is not found
            dict1[dia[0]+dia[1]] = np.array([]) # create a vector there
            dict1[dia[0]+dia[1]] = np.append(dict1[dia[0]+dia[1]],time) # add time value to list
    return dict1

def density(dict1, dig, val):
    if len(val)>2: # diagraph must have more than 2 instances
        kde = sm.nonparametric.KDEUnivariate(val) # run time vector through density function
        kde.fit(bw=nrd0(val))
        dict1[dig] = kde.evaluate(range(501)) # evaluate at 0-500 and add to attack profile
    return dict1

def nrd0(x): # function to caluclate bandwith of kernel using silverman's rule of thumb(same as bw.nrd0 in R)
    if (len(x) < 2):
        raise ValueError('Must have more than 2 values')
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

#gather filenames/paths to import data
os.system('cls' if os.name == 'nt' else 'clear') # clears previous terminal output for windows or unix-like systems
print "IMPORTING DATA"
print strftime("%H:%M:%S")
filepaths, namelists, CUdata, allUsers =[], [], [], []
dataPath = '/home/andrew/Documents/Research/keystroke-authentication/Formatted CU Data/' #location of formatted data files
for root, dirs, files in os.walk(dataPath, topdown=False): #obtains all files/directories in designated directory
    for name in files:
        filepaths.append(os.path.join(root,name)) #store paths to all files in directory
        namelists.append(name)
filepaths.sort()
namelists.sort()
namelist = []
allData = []
for no, path in enumerate(filepaths): #loop to open all files
    secondSplit = []
    datapath = open(path,'r')
    temp = datapath.read()
    firstSplit = temp.split('\t') # split at tabs, then at colons
    for s in firstSplit:
        splitString = s.strip('\n').split(':')
        secondSplit.append(splitString)
    if len(secondSplit)>12000:
        allData.append(secondSplit) # adds number only data to a list of lists only if containing more than 10k datapoints
        namelist.append(namelists[no])
    else:
        del namelists[no]
        del filepaths[no]
print "ORGANISING DATA"
print strftime("%H:%M:%S")
keys = []
userDia, userTime = [],[] # splits the data into two lists of lists
for datum in allData: # iterates through each user through a list of character/time pairs
    diaList, timeList = [],[]
    for loc,dat in enumerate(datum,start=0): # iterate every keystroke
        if (loc > 0) & (len(dat)>1) & (len(datum[loc-1])>1):
            if (dat[1].isdigit() and datum[loc-1][1].isdigit()):
                timediff = int(dat[1]) - int(datum[loc-1][1])
                if (timediff < 500) & (timediff>0): #check for less than 500ms and greater than 0ms
                    keys = [datum[loc-1][0],dat[0]]
                    diaList.append(keys) # add diagraphs to a list
                    timeList.append(float(timediff)) # add times to a list
    userDia.append(div(diaList,1000))
    userTime.append(div(timeList,1000))
profiles = [] # list to store the 20 profiles
for listdia,listtime in zip(userDia,userTime):
    proflist = [] # list to store each infdivdual profile, reset each loop
    for subdia,subtime in zip(listdia,listtime):
        profileDict = {} # create dictionary to store diagraph instances
        for dia,time in zip(subdia,subtime):
            profileDict = orgDiagraph(profileDict,dia,time)
        proflist.append(profileDict) # add dictionary to the list
    profiles.append(proflist) # add list to profile list
print "CREATING PROFILES"
print strftime("%H:%M:%S")
atktraining = []
atktesting = []
for prof in profiles: # iterate through all profiles
    atksubprof = []
    for lists in prof: # iterate through the 20 dictionaries
        atkProf = {} # dictionary to store test profiles for attack
        for dig,val in lists.items(): # iterate through all diagraphs
            atkProf = density(atkProf,dig,val)
        atksubprof.append(atkProf)
    atktraining.append(atksubprof[:(len(atksubprof)//2)])
    atktesting.append(atksubprof[(len(atksubprof)//2):])

newpath = '/home/andrew/Documents/Research/keystroke-authentication/results.csv'
finsumscore,findifscore,sumthresh,difthresh,sumfar,sumipr,diffar,difipr,sumatkscore,difatkscore = [],[],[],[],[],[],[],[],[],[] # lists to store data for prining to .csv
for useNum,udia,utime in zip(range(len(userDia)),userDia,userTime):
    print "USER %s PROFILE" % namelist[useNum][:7]
    print strftime("%H:%M:%S")
    userScores = [] # list to store results of verification testProfiles
    impostScores = [] # list to store results of impostor attacks
    userScores2 = [] # list to store results of second verificaiton
    impostScores2 = [] # list to store results of second attacks
    combine = list(itertools.islice(itertools.combinations(zip(udia,utime),10),200))
    for combos in combine: #iterate through all combinations
        refProf,reference = {},{}
        testing,training = {},{} # initializes list of user profiles
        testingProf,trainingProf = {},{}
        clist = map(list,combos) # store combos as a list instead of tuple
        for element,t in zip(udia,utime):
            if [element,t] not in clist: # check to see if an elemnt isnt in the comibation
                clist.append([element,t]) # add test profiles to last two indicies of the list
        for n,c in enumerate(clist): # iterate over the combination
            if n < 10: # iterate only though the combinations
                for s,a in zip(c[0],c[1]): # iterate through all diagraphs/times
                    refProf = orgDiagraph(refProf,s,a)
            elif n < (10+(len(clist)-10)//2): # grab first half of remaining data
                for s,a in zip(c[0],c[1]): # iterate through all diagraphs/times
                    trainingProf = orgDiagraph(trainingProf,s,a)
            else:
                for s,a in zip(c[0],c[1]): # iterate through all diagraphs/times
                    testingProf = orgDiagraph(testingProf,s,a)
        for dig,val in refProf.items(): # iterate through all diagraphs
            reference = density(reference,dig,val)
        for dig,val in trainingProf.items():
            training  = density(training,dig,val)
        for dig,val in testingProf.items():
            testing  = density(testing,dig,val)
        count = 0 # count of unique diagraphs shared between the test prof and the user prof
        score = 0 # a sum of differences between density plot for each test
        for i in training: # for all diagraphs in the test profile
            if i in reference: # if the diagraph exists in the reference profile
                sumval =  np.sum(np.absolute(reference[i]-training[i]))
                count += 1 # increment count
                score += sumval #add the difference between the two densities to the score
        if count != 0:
            userScores.append(score/count) # save average score to vector
        count = 0
        score = 0
        for j in testing: # for all diagraphs in the test profile
            if j in reference: # if the diagraph exists in the reference profile
                sumval =  np.sum(np.absolute(reference[j]-testing[j]))
                count += 1 # increment count
                score += sumval #add the difference between the two densities to the score"
        if count != 0:
            userScores2.append(score/count) # save average score to vector
        for atknum,atk in enumerate(atktraining): # iterate through all attack profiles
            if atknum != useNum: # ignore the profile that would result in verification
                count = 0
                score = 0
                for subatk in atk:
                    for k in subatk:
                        if k in reference:
                            sumval =  np.sum(np.absolute(reference[k]-subatk[k]))
                            count += 1
                            score += sumval
                    if count != 0:
                        impostScores.append(score/count)
        for atknum,atk in enumerate(atktesting): # iterate through all attack profiles
            if atknum != useNum: # ignore the profile that would result in verification
                count = 0
                score = 0
                for subatk in atk:
                    for k in subatk:
                        if k in reference:
                            sumval =  np.sum(np.absolute(reference[k]-subatk[k]))
                            count += 1
                            score += sumval
                    if count != 0:
                        impostScores2.append(score/count)
    cutoffs  = np.linspace((max(impostScores)+.002),(min(userScores)-.002),100)
    results = {}
    FAR  = np.array([])
    IPR  = np.array([])
    for i in range(len(cutoffs)):
        y = str(i)
        results['users'+y] = len(list(x for x in userScores if x <= cutoffs[i])) # users below threshold
        results['imposters'+y] = len(list(x for x in impostScores if x <= cutoffs[i])) # imposters below threshold
        FAR = np.append(FAR,(1-float(results['users'+y])/float(len(userScores)))*100)
        IPR = np.append(IPR,float(results['imposters'+y])/float(len(impostScores))*100)
    summed = FAR + IPR
    summin = np.argmin(summed)
    dif = abs(FAR-IPR)
    difmin= np.argmin(dif)
    finsumscore.append(len(list(x for x in userScores2 if x >= cutoffs[summin]))/float(len(userScores2)*100))
    findifscore.append(len(list(x for x in userScores2 if x >= cutoffs[difmin]))/float(len(userScores2)*100))
    sumatkscore.append(len(list(x for x in impostScores2 if x <= cutoffs[summin]))/float(len(impostScores2)*100))
    difatkscore.append(len(list(x for x in impostScores2 if x <= cutoffs[difmin]))/float(len(impostScores2)*100))
    sumthresh.append(cutoffs[summin])
    difthresh.append(cutoffs[difmin])
    sumfar.append(FAR[summin])
    sumipr.append(IPR[summin])
    diffar.append(FAR[difmin])
    difipr.append(IPR[difmin])
with open(newpath,'w') as outfile:
    a = csv.writer(outfile, delimiter=',')
    for x in range(len(sumfar)):
        a.writerow([namelist[x][:-4],
                    sumthresh[x],
                    sumfar[x],
                    sumipr[x],
                    finsumscore[x],
                    sumatkscore[x],
                    difthresh[x],
                    diffar[x],
                    difipr[x],
                    findifscore[x],
                    difatkscore[x]])
