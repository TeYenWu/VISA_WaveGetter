import matplotlib.pyplot as plt
import json
import os 
import sys

#filepath = os.path.join(os.getcwd(), args.element)
#if not os.path.exists(filepath):
#    os.mkdir(filepath)

#os.chdir(filepath)
sub_dirs = [o for o in os.listdir('./') if os.path.isdir(os.path.join('./',o))]

for sub_dir in sub_dirs:
    os.chdir(os.path.join(os.getcwd(), sub_dir))
    a = open('data.json','r')
    data = json.load(a)

    keys = data[0].keys()
    for key in keys:
        plt.plot(data[0][key]['wave'])
        plt.axis([0, 2000, -0.5, 0.5])
        plt.savefig(key)
        plt.clf()

    os.chdir('../')