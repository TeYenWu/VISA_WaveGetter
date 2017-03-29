import matplotlib.pyplot as plt
import json
import os 
import sys
from scipy.fftpack import dct


for root, dirs, files in os.walk(a):
	print count
	count += 1
	if  'data.json' in files:
		os.chdir(root)
		r = root.split('/')
		a = open(root + '/data.json','r')
		data = json.load(a)
		for index in range(len(data)):

keys = data[index].keys()
for key in keys:
	plt.plot(data[index][key]['wave'])
	plt.savefig(key+'_'+str(index))
	plt.clf()		


for i in range(len(p)):
     for j in range( len ( p[keys[i]] ) ):   
             a = p[keys[i]]['wave'][j]
             f.wrtie(a)
             f.wrtie(',')
     f.wrtie('\n')
 
