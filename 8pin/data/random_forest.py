import numpy as np
import random 
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
label = []
train_data = []
train_label = []
test_data =[]
test_label = []
train = np.genfromtxt(str(1) + '.csv',delimiter = ',')
for j in range(len(train)):
	label.append(0)

for i in xrange(1,6):
	d = np.genfromtxt(str(i+1) + '.csv',delimiter = ',')
	train = np.concatenate((train,d))
	for j in range(len(d)):
		label.append(i)

print label

c = zip(train,label)
random.shuffle(c)
train,label = zip(*c)


train_data = train[0: (len(train) * 3/4)]
test_data = train[(len(train) * 3/4): len(train)]
train_label = label[0: (len(label) * 3/4)]
test_label = label[(len(label) * 3/4): len(label)]

print "====start RFC======="

clf = RandomForestClassifier(50)
clf.fit(train_data,train_label)
scores = cross_val_score(clf, train, label, cv=10)

print scores

t = np.genfromtxt("train.csv",delimiter = ',')
print clf.predict(t)
#print clf.score(test_data,test_label)


