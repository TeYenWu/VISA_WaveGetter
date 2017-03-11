from sklearn import svm
from sklearn.externals import joblib
from math import ceil
import numpy as np
import pickle
import json
import os

from feature_extraction import get_wave_feature

class SVM():
    def __init__(self, model_dir='Model', data_dir='data', preTrained=False):
        self.model_dir = model_dir
        
        #SVM hyperparameter
        self.C = 1.0
        self.kernel = 'rbf'
        self.degree = 3
        self.gamma = 'auto'
        self.coef0 = 0.0
        self.tol = 0.001
        self.max_iter = -1

        if not preTrained:
            #load data and train
            self.model = svm.SVC(C=self.C, 
                                 kernel=self.kernel, 
                                 degree=self.degree,
                                 gamma=self.gamma,
                                 coef0=self.coef0,
                                 tol=self.tol,
                                 max_iter=self.max_iter)
            
            self.train_X, self.train_y, self.dev_X, self.dev_y, self.label_list, self.feature_order = self.data_proccess(data_dir)
            print(self.train_y)
            self.train()

        else:
            #load model
            self.load_model()

    def data_proccess(self, data_dir, dev_portion=0.05):
        label_list = []
        train_X, train_y, dev_X, dev_y = [], [], [], [] 
        
        sub_dirs = [o for o in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir,o))] 
        for idx in range(len(sub_dirs)):
            label_list.append(sub_dirs[idx])
            
            data = json.load(open(os.path.join(data_dir, sub_dirs[idx], 'data.json'), 'r'))
            
            dev_size = ceil(float(len(data)) * dev_portion)
            order = ['pos1_neg2_test1', 'pos1_neg2_test3', 'pos1_neg3_test1', 'pos1_neg3_test2', 'pos2_neg3_test1', 'pos2_neg3_test2']
            #order = ['pos1_neg2_test1']

            for d in data:
                features = np.array([])      
                for o in order:
                    features = np.concatenate((features, get_wave_feature(np.array(d[o]['wave']), 80000, 2000)), axis=0)# get wave feature not done

                #get data to validation set
                if dev_size > 0:
                    dev_X.append(features)
                    dev_y.append(idx)
                    dev_size -= 1
                else:
                    train_X.append(features)
                    train_y.append(idx)
        
        return np.array(train_X), np.array(train_y), np.array(dev_X), np.array(dev_y), label_list, order

                                

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
        train_acc = self.model.score(self.train_X, self.train_y)    
        print('training accurency: %f' % train_acc)

        #validation
        dev_acc = self.model.score(self.dev_X, self.dev_y)
        print('develop accurency: %f' % dev_acc)
        
        #dump model to model dir
        if not os.path.exists(os.path.join(os.getcwd(), self.model_dir)):
            print('%s doesn\'t exist, creating...')
            os.mkdir(self.model_dir)

        joblib.dump(self.model, os.path.join(self.model_dir, 'model.pkl'))
        json.dump({'label_list': self.label_list, 'feature_order': self.feature_order}, open(os.path.join(self.model_dir, 'config.json'), 'w'))

        print('model saved at: ./%s/' % self.model_dir)

    def test(self, test_waves):
        test_X = np.array([])
        for o in self.feature_order:
            test_X = np.concatenate((test_X, get_wave_feature(np.array(test_waves[o]['wave']), 80000, 2000)), axis=0)
            
        return self.label_list[self.model.predict(test_X)]

if __name__ == '__main__':
    SVM(model_dir='testModel', data_dir='3pin')



