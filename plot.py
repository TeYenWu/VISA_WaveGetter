import matplotlib.pyplot as plt
import json
import os 
import sys
filepath = os.path.join(os.getcwd(),sys.argv[1])
if not os.path.exists(filepath):
    os.mkdir(filepath)

os.chdir(filepath)


a = open('data.json','r')
data = json.load(a)

keys = data[0].keys()
for key in keys:
	plt.plot(data[0][key]['wave'])
	plt.savefig(key)
	plt.clf()