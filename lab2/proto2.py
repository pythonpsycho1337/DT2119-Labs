import numpy as np
from lab2.tools2 import *
from sklearn.mixture import gmm
import copy


def concatHMMs(hmmmodels, namelist):
    """ Concatenates HMM models in a left to right manner

    Args:
       hmmmodels: list of dictionaries with the following keys:
           name: phonetic or word symbol corresponding to the model
           startprob: M+1 array with priori probability of state
           transmat: (M+1)x(M+1) transition matrix
           means: MxD array of mean vectors
           covars: MxD array of variances
       namelist: list of model names that we want to concatenate

    D is the dimension of the feature vectors
    M is the number of states in each HMM model (could be different for each)

    Output
       combinedhmm: dictionary with the same keys as the input but
                    combined models

    Example:
       wordHMMs['o'] = concatHMMs(phoneHMMs, ['sil', 'ow', 'sil'])
    """
    wordHmm = dict2 = copy.deepcopy(hmmmodels[namelist[0]])
    d = 4*len(namelist)-(len(namelist)-1)
    wordHmm['transmat'] = np.zeros((d,d))
    wordHmm['means'] = np.zeros((3*len(namelist),13))
    wordHmm['covars'] = np.zeros((3*len(namelist), 13))
    wordHmm['startprob'] = np.zeros((1, 3*len(namelist)))
    wordHmm['startprob'][0,0] = 1
    for i in range(0,len(namelist)):
        c = i*3#c is the coordinate
        wordHmm['transmat'][c:c+4, c:c+4] = hmmmodels[namelist[i]]['transmat']
        wordHmm['means'][c:c+3,:] = hmmmodels[namelist[i]]['means']
        wordHmm['covars'][c:c + 3, :] = hmmmodels[namelist[i]]['covars']
    wordHmm['transmat'][-1, -1] = 1
    return wordHmm


def gmmloglik(log_emlik, weights):
    """Log Likelihood for a GMM model based on Multivariate Normal Distribution.

    Args:
        log_emlik: array like, shape (N, K).
            contains the log likelihoods for each of N observations and
            each of K distributions
        weights:   weight vector for the K components in the mixture

    Output:
        gmmloglik: scalar, log likelihood of data given the GMM model.
    """

    means, covars = weights
    likelihood = log_multivariate_normal_density_diag(log_emlik, means, covars)
    gmmloglik = np.log(likelihood)
    return gmmloglik

def forward(log_emlik, log_startprob, log_transmat, ref=None):
    """Forward (alpha) probabilities in log domain.

    Args:
        log_emlik: NxM array of emission log likelihoods, N frames, M states
        log_startprob: log probability to start in state i
        log_transmat: log transition probability from state i to j

    Output:
        forward_prob: NxM array of forward log probabilities for each of the M states in the model
    """
    observations = len(log_emlik)#Each row in log_emlik corresponds to one observation
    states = len(log_emlik[0])
    alpha = np.zeros((observations,states))

    for j in range(0,states):
        alpha[0,j] = log_startprob[0,j] + log_emlik[0,j]

    for i in range(1,observations):
        a1 = np.zeros((states,states))
        frame = np.zeros(states)
        for j in range(0, states):
            alpha[i,j] = logsumexp(alpha[i-1,:] + log_transmat[:,j]) + log_emlik[i,j]

    return alpha

def forward_mat(log_emlik, log_startprob, log_transmat, ref=None):
    """Forward (alpha) probabilities in log domain.

    Args:
        log_emlik: NxM array of emission log likelihoods, N frames, M states
        log_startprob: log probability to start in state i
        log_transmat: log transition probability from state i to j

    Output:
        forward_prob: NxM array of forward log probabilities for each of the M states in the model
    """
    alpha = log_startprob + log_emlik[0]
    alpha_tmp = [alpha]

    for frame in log_emlik[1:]:
        a1 = alpha.reshape((9,1)) + log_transmat
        nn = log_transmat - a1
        a2 = logsumexp(a1, axis=1)
        alpha = a2 + frame
        alpha_tmp.append(alpha)
    alpha = np.vstack(alpha_tmp)
    return alpha

def backward(log_emlik, log_startprob, log_transmat):
    """Backward (beta) probabilities in log domain.

    Args:
        log_emlik: NxM array of emission log likelihoods, N frames, M states
        log_startprob: log probability to start in state i
        log_transmat: transition log probability from state i to j

    Output:
        backward_prob: NxM array of backward log probabilities for each of the M states in the model
    """

    beta = np.zeros(log_startprob.shape)
    b_prob = [beta]
    for frame in np.flip(log_emlik[1:], axis=0):
        logsum = frame + beta + log_transmat
        beta = logsumexp(logsum, axis=1)
        b_prob.append(beta)

    p_backward = np.flip(np.vstack(b_prob), axis=0)
    return p_backward

def viterbi(log_emlik, log_startprob, log_transmat):
    """Viterbi path.

    Args:
        log_emlik: NxM array of emission log likelihoods, N frames, M states
        log_startprob: log probability to start in state i
        log_transmat: transition log probability from state i to j

    Output:
        viterbi_loglik: log likelihood of the best path
        viterbi_path: best path
    """
    observations = len(log_emlik)  # Each row in log_emlik corresponds to one observation
    states = len(log_emlik[0])
    V = np.zeros((observations, states))
    B = np.zeros((observations,states))

    #Initialize first row of V
    V[0, :] = log_startprob[0, :] + log_emlik[0, :]

    #Propagate best paths foward
    for o in range(1, observations):
        V[o,:] = np.max(V[o - 1, :, None] + log_transmat[:, :], axis=0) + log_emlik[o, :]
        B[o,:] = np.argmax(V[o - 1, :, None] + log_transmat[:, :], axis=0)

    lenOfShortest = np.max(V[-1, :])

    #Extract best path
    state = int(np.argmax(V[-1,:]))
    bestPath = [state]
    for o in range(observations-1, 0, -1):
        state = int(B[o,state])
        bestPath = [state] + bestPath

    #Return in same format as in the example
    return (lenOfShortest,np.array(bestPath))


def statePosteriors(log_alpha, log_beta):
    """State posterior (gamma) probabilities in log domain.

    Args:
        log_alpha: NxM array of log forward (alpha) probabilities
        log_beta: NxM array of log backward (beta) probabilities
    where N is the number of frames, and M the number of states

    Output:
        log_gamma: NxM array of gamma probabilities for each of the M states in the model
    """
    return log_alpha + log_beta - logsumexp(log_alpha[-1])


def updateMeanAndVar(X, log_gamma, varianceFloor=5.0):
    """ Update Gaussian parameters with diagonal covariance

    Args:
         X: NxD array of feature vectors
         log_gamma: NxM state posterior probabilities in log domain
         varianceFloor: minimum allowed variance scalar
    were N is the lenght of the observation sequence, D is the
    dimensionality of the feature vectors and M is the number of
    states in the model

    Outputs:
         means: MxD mean vectors for each state
         covars: MxD covariance (variance) vectors for each state
    """
    gamma = np.exp(log_gamma)
    prod = X[:,None,:] * gamma[:,:, None]

    normalize = np.sum(gamma,axis=0)[:,None]
    summed = np.sum(prod,axis=0)
    means = summed / normalize

    naivemeans = np.mean(prod, axis=0)

    diff1 = X[:,None,:]-means[None,...]
    diff2 = diff1**2
    diff3 = diff2 * gamma[...,None]
    summed = np.sum(diff3, axis=0)
    covars = np.maximum(summed/normalize, varianceFloor)

    return means, covars


def baum_welch(lmfcc, init_means, init_covars,  log_startprob, log_trans, example_data, max_iter=20, stop_threshold=1.0):
    means = init_means
    covars = init_covars
    log_alpha_lik = -10000000000000
    for i in range(max_iter):
        loglikelihood = log_multivariate_normal_density_diag(lmfcc, means, covars)
        log_alpha = forward(loglikelihood, log_startprob, log_trans)
        log_beta = backward(loglikelihood, log_startprob, log_trans)
        log_gamma = statePosteriors(log_alpha, log_beta)
        means, covars = updateMeanAndVar(lmfcc, log_gamma)

        _new_lik = logsumexp(log_alpha[-1])
        if (_new_lik - log_alpha_lik) < stop_threshold:
            break
        log_alpha_lik = _new_lik
        print('iter ',i,' likelihood', np.mean(log_alpha_lik))

    print("Baum Welch Done!")



