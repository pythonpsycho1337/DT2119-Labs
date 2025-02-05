import numpy as np
import keras
from keras.models import Sequential
from keras.layers.core import Activation, Dense
import matplotlib.pyplot as plt
from StandardiseData import standardize_per_utterance, lmfcc_stack, standardize_per_training_set, get_training_and_validation_sets
from confusion_mat import plot_confusion_matrix, get_confusion_matrix
import pickle

def combinePhonemes(labels,stateList):
    #labels - one dimensional tensor where each element is an observation
    spIndex = -1
    for i in range(0,len(stateList.keys())):
        if stateList[i] == 'sp_0':
            spIndex = i

    labels[labels > spIndex] += 2
    labels = np.floor(labels/3)
    labels = labels.astype("int")

    return labels


NUM_STACK = 5

statlist = pickle.load(open('stateList.pkl', 'rb'))
p = np.load('predicted_test.npy')

train, validation = get_training_and_validation_sets(np.load('G:/train_data.npz')['data'])
_, __, test_data = standardize_per_training_set(train, [], np.load('G:/test_data.npz')['data'])

print('processing data for input')
x = [lmfcc_stack(d['lmfcc'], NUM_STACK) for d in test_data]
x = np.vstack(x)
y = [d['targets'] for d in test_data]
y = np.hstack(y).T


predicted = p.argmax(axis=1)
label = y.argmax(axis=1)
cm = get_confusion_matrix(predicted, label)
# manually normalize sil_0 and sil_1
cm[39, 39] = 0
cm[40, 40] = 0
plot_confusion_matrix(cm, statlist)

# model = keras.models.load_model('h3_adagrad_relu_u256_e100.h5py')
# print('predicting..')
# p = model.predict(x)
print('hello world')