import scipy as sp
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.mlab as mlab
import os
from matplotlib import cm
#gather filenames/paths to import data
def nrd0(x): # function to caluclate bandwith of kernel (same as bw.nrd0 in R)
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

namelist = [] # list of filenames
print "IMPORTING DATA"
filepaths, CUdata, allUsers =[], [], []
dataPath = '/home/andrew/Documents/Research/keystroke-authentication/keystroke goats/filtered/' #location of formatted data files
for root, dirs, files in os.walk(dataPath, topdown=False): #obtains all files/directories in designated directory
    for name in files:
        if name in {'4486493.txt','ADzagrobs.txt'}
        filepaths.append(os.path.join(root,name)) #store paths to all files in directory
        namelist.append(name)
filepaths.sort()
namelist.sort()
i = 0
for path in filepaths: #loop to open all files
    datapath = open(path,'r')
    CUdata.append(datapath.read())
    allUsers.append(CUdata[i]) # put data into a list of lists
    i += 1

allData = []
print "ORGANISING DATA"
# converting sublist into string to split at commas and colons
for data in allUsers:
    datastr = ""
    secondSplit = []
    datastr = datastr.join(str(x) for x in data)
    firstSplit = datastr.split('\t')
    for s in firstSplit:
        splitString = s.strip('\r\n').split(':')
        secondSplit.append(splitString)
    allData.append(secondSplit) # adds number only data to a list of lists
keys = [] # list to hold diagraphs
userDia, userTime = [],[] # 2 lists to hold all times and diagraphs
for datum in allData: #
    diaList, timeList = [],[]
    for loc,dat in enumerate(datum,start=0): # iterate every keystroke
        if (loc > 0) & (len(dat)>1):
            if (dat[1][:4] == '6355') | (dat[1][:4] == '6356'):
                timediff = int(dat[1]) - int(datum[loc-1][1])
                if (timediff < 500) & (timediff>0): #check for less than 500ms and greater than 0ms
                    keys = [datum[loc-1][0],dat[0]]
                    diaList.append(keys) # add diagraphs to a list
                    timeList.append(float(timediff)) # add times to a list
            elif (len(dat[1])>12):
                timediff = int(dat[1]) - int(datum[loc-1][1])
                if (timediff < 500) & (timediff>0): #check for less than 500ms and greater than 0ms
                    keys = [datum[loc-1][0],dat[0]]
                    diaList.append(keys) # add diagraphs to a list
                    timeList.append(float(timediff)) # add times to a list
            else:
                timediff = int(dat[1][:9]) - int(datum[loc-1][1][:9])
                if (timediff < 500) & (timediff>0): #check for less than 500ms and greater than 0ms
                    keys = [datum[loc-1][0],dat[0]]
                    diaList.append(keys) # add diagraphs to a list
                    timeList.append(float(timediff)) # add times to a list
    userDia.append((diaList))
    userTime.append((timeList))
profiles = [] # list to store the 20 profiles
for listdia,listtime in zip(userDia,userTime):
    profileDict = {} # create dictionary to store diagraph instances
    for dia,time in zip(listdia,listtime):
        if len(dia)>1:
            if dia[0]+dia[1] in profileDict: # index dictionary at diagraph, check if it exists
                profileDict[dia[0]+dia[1]].append(time) # add time value to list
            else: # if the the index is not found
                profileDict[dia[0]+dia[1]] = [] # create a list there
                profileDict[dia[0]+dia[1]].append(time) # add time value to list
    profiles.append(profileDict) # add list to profile list
commonDiagraphs = open('/home/andrew/Documents/Research/keystroke-authentication/keystroke goats/DIAGRAPHS_ETC.txt')
diagraphsToTest = commonDiagraphs.read()
allTestDia = diagraphsToTest.rstrip('\n').split(' ')
#diagraphToTest = raw_input("Enter the diagraph to visualize: ")
#numberOfUsers = raw_input("Enter the number of users you would like to test: ") # UNCOMMENT FOR LARGER SET
testUserList = []
colormap = cm.nipy_spectral(np.linspace(0,.9,len(profiles)))
for number,diagraphToTest in enumerate(allTestDia):
    plt.figure(number)
    if len(diagraphToTest) == 1:
        diagraphToTest = " " + diagraphToTest
    for numUsers,uname in enumerate(namelist):
        testUserList.append(numUsers)#raw_input("Enter user " + str(numUsers) + ": ")) #UNCOMMENT FOR LARGER SET
        timeToTest = [] # list to contain all times for a given diagraph for user
        timeToCompare = [] # list for times to compare to
        if diagraphToTest in profiles[numUsers]:
            for instance in profiles[numUsers][diagraphToTest]:
                timeToTest.append(instance)
        if len(timeToTest)>1:
            #kde = stats.kde.gaussian_kde(timeToTest)
            kde = sm.nonparametric.KDEUnivariate(timeToTest) # calculate density function for all times for given diagraph
            kde.fit(bw=nrd0(timeToTest))
            kp = range(500) # range of 500 points
            func = kde.evaluate(kp)
            kdex = lambda x: kde.evaluate(x)*x # caluclate expectation
            expect, error = sp.integrate.quad(kdex,0,500)
            plt.plot(kp,func,label = "%s" % uname[:-4],linewidth = 2,color = colormap[numUsers]) # plot density function at 0-500
            plt.plot([expect]*2,[0,kde.evaluate(expect)],color = colormap[numUsers],ls = '--')
            plt.legend() # make graph pretty
            plt.ylabel('Density')
            plt.xlabel('Time (ms)')
            plt.title("Density Comparison for Diagraph '" + diagraphToTest + "'")
    plt.savefig('/home/andrew/Documents/Research/SharedDiagraphs/' + diagraphToTest + '.png') #save to folder
    plt.close()
