import numpy as np
import matplotlib.pyplot as plt
from StandardiseData import standardize_per_utterance, lmfcc_stack, standardize_per_training_set, get_training_and_validation_sets
from confusion_mat import plot_confusion_matrix, get_confusion_matrix
import pickle

NUM_STACK = 5

statlist = pickle.load(open('stateList.pkl', 'rb'))
p = np.load('predicted_test.npy')

train, validation = get_training_and_validation_sets(np.load('train_data.npz')['data'])
_, __, test_data = standardize_per_training_set(train, [], np.load('test_data.npz')['data'])

print('processing data for input')
x = [lmfcc_stack(d['lmfcc'], NUM_STACK) for d in test_data]
x = np.vstack(x)
y = [d['targets'] for d in test_data]
y = np.hstack(y).T


predicted = p.argmax(axis=1)
label = y.argmax(axis=1)
z = predicted[predicted > 32] + 2

cm = get_confusion_matrix(predicted, label)
# manually normalize sil_0 and sil_1
# cm[39, 39] = 0
# cm[40, 40] = 0
print('calculating accuracy')
accuracy = 1 - np.count_nonzero(predicted - label) / predicted.shape[0]
print(accuracy * 100, '%')
plot_confusion_matrix(cm, statlist, title='Frame by frame state confusion mat',save=True)


# model = keras.models.load_model('h3_adagrad_relu_u256_e100.h5py')
# print('predicting..')
# p = model.predict(x)
print('hello world')