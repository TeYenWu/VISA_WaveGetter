import matplotlib.pyplot as plt
import json
import os 
import sys
from scipy.fftpack import fft
import numpy as np

keys = [u'pos2_neg3_test1', u'pos2_neg3_test2', u'pos1_neg3_test1', u'pos1_neg3_test2', u'pos1_neg2_test1', u'pos1_neg2_test3']
one_hot = [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]]

train = []

a = open('data.json','r')
data = json.load(a)
for index in range(len(data)):
	line = []
	keys = data[index].keys()
	for key in keys:
		t = data[index][key]['wave']
		f = np.abs(fft(data[index][key]['wave']))
		line.append(np.mean(f))
		line.append(np.mean(t))
		line.append(np.std(f))
		line.append(np.std(t))
		line.append(np.var(f))
		line.append(np.var(t))
		line.append(np.amax(f))
		line.append(np.amax(t))
		line.append(np.amin(f))
		line.append(np.amin(t))
		line.append(np.median(f))
		line.append(np.median(t))

	train.append(line)

print len (train)
with open('train.csv','w') as csv:
	for i in range(len(train)):
		for index in range(len(train[0])):
			csv.write(str(train[i][index]))
			if index != len(train[0]) -1:
				csv.write(',')
		csv.write('\n')		


