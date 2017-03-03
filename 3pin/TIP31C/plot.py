import matplotlib.pyplot as plt
import json
import os 

filepath = os.path.join(os.getcwd(), args.element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

os.chdir(filepath)


a = open(sys.argv[1] + 'data.json','r')
data = json.load(a)

keys = data[0].keys()
for key in keys:
	plt.plot(data[0][key]['wave'])
	plt.savefig(key)
	plt.clf()