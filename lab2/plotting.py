import matplotlib.pyplot as plt
import numpy as np


def plotEachStep(lmfcc_example,loglikelihood,log_alpha,log_beta,log_gamma):
    plt.figure(figsize=(10,10))
    ax = plt.subplot(5, 1, 1)
    plt.yticks(np.arange(0, 12+1, 1.0))
    ax.set_title('lmfcc: Liftered MFCCs')
    ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12])
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    ax.set_xticklabels([])
    plt.pcolormesh(np.transpose(lmfcc_example))

    ax = plt.subplot(5, 1, 2)
    plt.yticks(np.arange(0, 8+1, 1.0))
    plt.title('obsloglik: HMM log likelihood of observation given the state')
    ax.set_yticklabels([0,1,2,3,4,5,6,7,8])
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    ax.set_xticklabels([])
    plt.pcolormesh(np.transpose(loglikelihood))

    ax = plt.subplot(5, 1, 3)
    plt.yticks(np.arange(0, 8+1, 1.0))
    ax.set_title('logalpha: forward log probabilities')
    ax.set_yticklabels([0,1,2,3,4,5,6,7,8])
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    ax.set_xticklabels([])
    plt.pcolormesh(np.transpose(log_alpha))

    ax = plt.subplot(5, 1, 4)
    plt.yticks(np.arange(0, 8+1, 1.0))
    ax.set_title('logbeta: backward log probabilities')
    ax.set_yticklabels([0,1,2,3,4,5,6,7,8])
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    ax.set_xticklabels([])
    plt.pcolormesh(np.transpose(log_beta))

    ax = plt.subplot(5, 1, 5)
    plt.yticks(np.arange(0, 8+1, 1.0))
    ax.set_title('loggamma: state log posteriors')
    ax.set_yticklabels([0,1,2,3,4,5,6,7,8])
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    ax.set_xticklabels([])
    plt.pcolormesh(np.transpose(log_gamma))
    return plt


