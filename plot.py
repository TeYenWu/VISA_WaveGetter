import matplotlib.pyplot as plt
import json
import os 
import sys
count = 0
for root, dirs, files in os.walk(os.getcwd()):
	if count == 0:
		continue
	a = open(root + '/data.json','r')
	data = json.load(a)
	for index in range(5):

		keys = data[index].keys()
		for key in keys:
			plt.plot(data[index][key]['wave'])
			plt.savefig(key)
			plt.clf()
	count+=1		