import numpy as np
import os
import statsmodels.api as sm
import sys
import csv
import itertools
import scipy
from scipy import stats
from time import strftime


def chunk(list1, num):  # function to split a list into roughly equal parts
    avg = len(list1) / float(num)
    out = [list1[i*avg:(i+1)*avg] for i in range(num)]
    return out

def div(l, n):
    n = max(1, n)
    last = [l[i:i + n] for i in range(0, len(l), n)]
    if len(last[-1])<(n):
        del last[-1]
    return last

def orgDiagraph(dict1,dia ,time): # function to orgainze diagraphs into dictionary
    if len(dia)>1:
        if dia[0]+dia[1] in dict1: # index dictionary at diagraph, check if it exists
            dict1[dia[0]+dia[1]] = np.append(dict1[dia[0]+dia[1]],time) # add time value to list
        else: # if the the index is not found
            dict1[dia[0]+dia[1]] = np.array([]) # create a vector there
            dict1[dia[0]+dia[1]] = np.append(dict1[dia[0]+dia[1]],time) # add time value to list
    return dict1

def density(dict1,dig, val):
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
userDia, userTime = [],[] # splits the data into two lists of lists
diaList,timeList = [],[]
for no, path in enumerate(filepaths): #loop to open all files
    secondSplit = []
    datapath = open(path,'r')
    temp = datapath.read()
    firstSplit = temp.split('\t') # split at tabs, then at colons
    for s in firstSplit:
        splitString = s.strip('\n').split(':')
        secondSplit.append(splitString)
    print len(secondSplit)//1000
    if len(secondSplit)>12000: # if user has more that 12k data points, then use them
        namelist.append(namelists[no])
        diaList, timeList = [],[]
        for loc,dat in enumerate(secondSplit,start=0): # iterate every keystroke
            if (loc > 0) & (len(dat)>1) & (len(secondSplit[loc-1])>1):
                if (dat[1].isdigit() and secondSplit[loc-1][1].isdigit()):
                    timediff = int(dat[1]) - int(secondSplit[loc-1][1])
                    if (timediff < 500) & (timediff>0): #check for less than 500ms and greater than 0ms
                        keys = [secondSplit[loc-1][0],dat[0]]
                        diaList.append(keys) # add diagraphs to a list
                        timeList.append(float(timediff)) # add times to a list
        userDia.append(div(diaList,1000)) # add times/diagraphs to lists in sets of 1000
        userTime.append(div(timeList,1000))
print "CREATING ATTACK PROFILES"
print strftime("%H:%M:%S")
keys = []
atktraining,atktesting,atksubprof = [],[],[]
profiles = [] # list to store the 20 profiles
for listdia,listtime in zip(userDia,userTime):
    proflist = [] # list to store each infdivdual profile, reset each loop
    for subdia,subtime in zip(listdia,listtime):
        profileDict = {} # create dictionary to store diagraph instances
        for dia,time in zip(subdia,subtime):
            profileDict = orgDiagraph(profileDict,dia,time)
        proflist.append(profileDict) # add dictionary to the list
    profiles.append(proflist) # add list to profile list"
print strftime("%H:%M:%S")
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

avgsumthresh,avgsumfar,avgsumipr,avgfinsumscore,avgsumatkscore,avgdifthresh,avgdiffar,avgdifipr,avgfindifscore,avgdifatkscore = [],[],[],[],[],[],[],[],[],[]
for useNum,udia,utime in zip(range(len(userDia)),userDia,userTime):
    finsumscore,findifscore,sumthresh,difthresh,sumfar,sumipr,diffar,difipr,sumatkscore,difatkscore = [],[],[],[],[],[],[],[],[],[] # lists to store data for prining to .csv
    print "USER %s PROFILE" % namelist[useNum][:7]
    print strftime("%H:%M:%S")
    avguscore1,avguscore2,avgiscore1,avgiscore2 = [],[],[],[]
    combine = list(itertools.islice(itertools.combinations(zip(udia,utime),len(udia)-2),100))
    for combo in combine: #iterate through all combinations
        userScores,impostScores,userScores2,impostScores2 = [],[],[],[] # lists to store results of verification
        finrefprof,finref = {},{}
        testing,testingProf = {},{} # initializes list of user profiles
        clist = map(list,combo) # store combos as a list instead of tuple
        for element,t in zip(udia,utime):
            if [element,t] not in clist: # check to see if an elemnt isnt in the comibation
                clist.append([element,t]) # add test profiles to last two indicies of the list
        l = (len(clist))-2
        trainData = clist[:l]
        testData = clist[l:]
        combo2 = list(itertools.islice(itertools.combinations(trainData,l-2),10))
        for c in clist:
            for s,a in zip(c[0],c[1]):
                testingProf = orgDiagraph(testingProf,s,a)
        for dig,val in testingProf.items():
            testing  = density(testing,dig,val)
        for combos in combo2:
            clist2 = map(list,combos)
            for e in clist:
                if e not in clist2:
                    clist2.append(e)
            refProf,reference = {},{}
            training,trainingProf = {},{}
            for n,c in enumerate(clist2): # iterate over the combination
                if n < l-2:
                    for s,a in zip(c[0],c[1]): # iterate through all diagraphs/times
                        refProf = orgDiagraph(refProf,s,a)
                else:
                    for s,a in zip(c[0],c[1]): # iterate through all diagraphs/times
                        trainingProf = orgDiagraph(trainingProf,s,a)
            for dig,val in refProf.items(): # iterate through all diagraphs
                reference = density(reference,dig,val)
            for dig,val in trainingProf.items():
                training  = density(training,dig,val)
            userScores.append(difference(reference,training))
            for atknum,atk in enumerate(atktraining): # iterate through all attack profiles
                if atknum != useNum: # ignore the profile that would result in verification
                    for atk2 in atk:
                        impostScores.append(difference(atk2,reference))
        for tr in trainData:
            for s,a in zip(tr[0],tr[1]):
                finrefprof = orgDiagraph(finrefprof,s,a)
        for dig,val in finrefprof.items():
            finref = density(finref,dig,val)
        userScores2.append(difference(finref,testing)) # save average score to vector
        for atknum,atk in enumerate(atktesting): # iterate through all attack profiles
            if atknum != useNum: # ignore the profile that would result in verification
                for atk2 in atk:
                    impostScores2.append(difference(finref,atk2))
        cutoffs  = np.linspace((max(impostScores)+.002),(min(userScores)-.002),100)
        results = {}
        FAR  = np.array([])
        IPR  = np.array([])
        for i in range(len(cutoffs)):
            y = str(i)
            results['users'+y] = len(list(x for x in userScores if x <= cutoffs[i])) # users below threshold
            results['impostors'+y] = len(list(x for x in impostScores if x <= cutoffs[i])) # impostors below threshold
            FAR = np.append(FAR,(1-float(results['users'+y])/float(len(userScores)))*100)
            IPR = np.append(IPR,float(results['impostors'+y])/float(len(impostScores))*100)
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
    print sum(sumthresh)/float(len(sumthresh))
    print sum(difthresh)/float(len(sumthresh))
    avgsumthresh.append(sum(sumthresh)/float(len(sumthresh)))
    avgsumipr.append(sum(sumipr)/float(len(sumipr)))
    avgsumfar.append(sum(sumfar)/float(len(sumfar)))
    avgfinsumscore.append(sum(finsumscore)/float(len(finsumscore)))
    avgsumatkscore.append(sum(sumatkscore)/float(len(sumatkscore)))
    avgdifthresh.append(sum(difthresh)/float(len(difthresh)))
    avgdiffar.append(sum(diffar)/float(len(diffar)))
    avgdifipr.append(sum(difipr)/float(len(difipr)))
    avgfindifscore.append(sum(findifscore)/float(len(findifscore)))
    avgdifatkscore.append(sum(difatkscore)/float(len(difatkscore)))
with open(newpath,'w') as outfile:
    a = csv.writer(outfile, delimiter=',')
    for x in range(len(namelist)):
        a.writerow([namelist[x][:-4],
                    avgsumthresh[x],
                    avgsumfar[x],
                    avgsumipr[x],
                    avgfinsumscore[x],
                    avgsumatkscore[x],
                    avgdifthresh[x],
                    avgdiffar[x],
                    avgdifipr[x],
                    avgfindifscore[x],
                    avgdifatkscore[x]])
