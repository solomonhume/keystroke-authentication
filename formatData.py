import os
import base64


dataPath = '/home/andrew/Documents/Research/keystroke-authentication/cleaned_cu_data/'
filenames = []
filepaths = []

for root, dirs, files in os.walk(dataPath, topdown=False):
    for name in files:
        if name[0] != '.':
            filepaths.append(os.path.join(root,name))
            filenames.append(name)

filepaths.sort()
filenames.sort()
data = []
dataToBeTruncated = []
allData = []
k = 0
for path in filepaths:
	datapath = open(path,'r')
	data.append(datapath.read())
	k = k+1
	i = 0
	truncatedData = []
	for s in data[k-1].split('\n'):
		truncatedData.append(s[40:].strip())
		truncatedData[i] = truncatedData[i].replace('\r','')
		i = i+1
	del truncatedData[-1]
	allData.append(truncatedData)
allUsers = []
for data in allData:
    datastr = ""
    secondSplit = []
    datastr = datastr.join(str(x) for x in data)
    firstSplit = datastr.split(',')
    for s in firstSplit:
        splitString = s.split(':')
        secondSplit.append(splitString)
    allUsers.append(secondSplit) # adds number only data to a list of lists

dataSet = []
for datum in allUsers: # one list contains lists of times, the other lists of diagraphs
    dataSets = []
    for dat in datum: # iterate every two elements of data
        if (len(dat) == 4): #& (dat[0] == '1'):
            if (int(dat[1],16) > 20):
                dataSets.append(str(base64.b16decode(dat[1].upper()))+":"+dat[2])
    dataSet.append(dataSets)
newpath =  '/home/andrew/Documents/Research/keystroke-authentication/Formatted CU Data/'
j = 0
for name in filenames:
    with open(newpath+name,'w+') as newfile:
        for entry in dataSet[j]:
            newfile.write('%s\t' % entry)
    j = j+1
