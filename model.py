from sklearn import svm
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.externals import joblib
from math import ceil
from scipy.fftpack import fft

import numpy as np
import matplotlib.pyplot as plt

import random
import pickle
import json
import os

from feature_extraction import get_wave_feature

class RF():
    def __init__(self, model_dir='Model', data_dir='data', preTrained=False, withTest=False):
        self.model_dir = model_dir
        
        #SVM hyperparameter
        self.C = 1.0
        self.kernel = 'precomputed'
        self.degree = 3
        self.gamma = 'auto'
        self.coef0 = 0.0
        self.tol = 0.001
        self.max_iter = -1
        
        self.withTest = withTest

        if not preTrained:
            #load data and train
            #self.model = svm.SVC(C=self.C, 
            #                     kernel=self.kernel, 
            #                     degree=self.degree,
            #                     gamma=self.gamma,
            #                     coef0=self.coef0,
            #                     tol=self.tol,
            #                     max_iter=self.max_iter)
            self.model = RandomForestClassifier(50)

            self.train_X, self.train_y, self.dev_X, self.dev_y, self.test_X, self.test_y, self.label_list, self.feature_order = self.data_proccess(data_dir)
            self.train()

        else:
            #load model
            self.load_model()

    def data_proccess(self, data_dir, dev_portion=0.2):
        label_list = []
        order = None
        train_X, train_y, dev_X, dev_y, test_X, test_y = [], [], [], [], [], [] 
        print('preparing training and develop data ...')
        sub_dirs = [o for o in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir,o))] 
        for idx in range(len(sub_dirs)):
            #label = sub_dirs[idx]
            label = sub_dirs[idx].split('_')[0]
            if label not in label_list:
                label_list.append(label)

            label_id = label_list.index(label)
            #label_list.append(sub_dirs[idx])
            
            data = json.load(open(os.path.join(data_dir, sub_dirs[idx], 'data.json'), 'r'))
            random.shuffle(data)
            
            dev_size = ceil(float(len(data)) * dev_portion)
            #order = ['pos1_neg2_test1', 'pos1_neg2_test3', 'pos1_neg3_test1', 'pos1_neg3_test2', 'pos2_neg3_test1', 'pos2_neg3_test2']
            #order = ['pos1_neg2_test1', 'pos1_neg2_test2']
            if order == None:
                order = data[0].keys() 
            
            print('data size of %s: %d' % (sub_dirs[idx], len(data)))
            for d in data: 
                features = np.array([])      
                for o in order:
                    features = np.concatenate((features, get_wave_feature(np.array(d[o]['wave']), 80000, 2000)), axis=0)

                #get data to validation set
                if dev_size > 0:
                    dev_X.append(features)
                    dev_y.append(label_id)
                    dev_size -= 1
                else:
                    train_X.append(features)
                    train_y.append(label_id)
        if not self.withTest:
            return np.array(train_X), np.array(train_y), np.array(dev_X), np.array(dev_y), np.array(test_X), np.array(test_y), label_list, order
        print('preparing test data ...')
        sub_dirs = [o for o in os.listdir(data_dir + '-test') if os.path.isdir(os.path.join(data_dir + '-test', o))]

        for idx in range(len(sub_dirs)):
            label = sub_dirs[idx].split('_')[0]
            if label not in label_list:
                print "label must in label list"
                continue
            
            label_id = label_list.index(label)
            
            data = json.load(open(os.path.join(data_dir + '-test', sub_dirs[idx], 'data.json'), 'r'))
            print('data size of %s: %d' % (sub_dirs[idx], len(data))) 
            for d in data:
                features = np.array([])
                for o in order:
                    features = np.concatenate((features, get_wave_feature(np.array(d[o]['wave']), 80000, 2000)), axis=0)

                test_X.append(features)
                test_y.append(label_id)
        
        return np.array(train_X), np.array(train_y), np.array(dev_X), np.array(dev_y), np.array(test_X), np.array(test_y), label_list, order

    def load_model(self):
        if not os.path.exists(os.path.join(os.getcwd(), self.model_dir)): 
            print('%s doesn\'t exist...')
            return

        self.model = joblib.load(os.path.join(self.model_dir, 'model.pkl'))
        config = json.load(open(os.path.join(self.model_dir, 'config.json'), 'r'))
        self.label_list = config['label_list']
        self.feature_order = config['feature_order']

    def train(self):
        self.model.fit(self.train_X, self.train_y)

        #train accurency
        print(self.train_X.shape)
        train_acc = self.model.score(self.train_X, self.train_y)    
        print('training accurency: %f' % train_acc)

        #validation
        print(self.dev_X.shape)
        dev_acc = self.model.score(self.dev_X, self.dev_y)
        print('develop accurency: %f' % dev_acc)
        
        #blind test
        if self.withTest:
            print(self.test_X.shape)
            test_acc = self.model.score(self.test_X, self.test_y)
            print('test accurency: %f' % test_acc)
        
        #dump model to model dir
        if not os.path.exists(os.path.join(os.getcwd(), self.model_dir)):
            print('%s doesn\'t exist, creating...' % self.model_dir)
            os.mkdir(self.model_dir)

        joblib.dump(self.model, os.path.join(self.model_dir, 'model.pkl'))
        json.dump({'label_list': self.label_list, 'feature_order': self.feature_order}, open(os.path.join(self.model_dir, 'config.json'), 'w'))

        print('model saved at: ./%s/' % self.model_dir)

    def test(self, test_waves):
        test_X = np.array([])
        for o in self.feature_order:
            test_X = np.concatenate((test_X, get_wave_feature(np.array(test_waves[o]['wave']), 80000, 2000)), axis=0)
            
        #print(self.model.predict(test_X))
        self.model.predict(np.array([test_X]))[0]
        return self.label_list[self.model.predict(np.array([test_X]))[0]]

if __name__ == '__main__':

    model = RF(model_dir='2pin_Model_2V', data_dir='2-pin-2V', preTrained=False, withTest=False)
    '''
    sub_dirs = [o for o in os.listdir('2-pin_test') if os.path.isdir(os.path.join('2-pin_test',o))]
    error = 0
    total = 0
    for sub_dir in sub_dirs:
        data = json.load(open(os.path.join('2-pin_test', sub_dir, 'data.json'), 'r'))
        for d in data:
            predict = model.test(d)
            #print('model predict %s: %s' % (sub_dir, predict))
            total += 1
            if sub_dir.split('_')[0] != predict:    
                print('model predict %s: %s' % (sub_dir, predict))
                error += 1
    
    print('test accurency: %f' % (float(total - error) / total))
    '''


