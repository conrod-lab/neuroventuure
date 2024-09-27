import numpy as np
import pandas as pd
from bct.utils import BCTParamError, binarize, get_rng
from bct.utils import pick_four_unique_nodes_quickly
#from bct.algorithms.reference import null_model_und_sign
from bct.algorithms import randmio_dir



#this  function was to create dummy undirected connectivity matrix and community affiliation vector to test the participation_coef_norm function
def generate_dummy_data(num_nodes, num_communities):
    # Generate random undirected connectivity matrix from -1 to 1

    W = np.random.rand(num_nodes, num_nodes)  # Generate random values
    W = (W + W.T) / 2  # Make the matrix symmetric to ensure undirectedness
    W = (W > 0.5).astype(int)  # Threshold to get binary matrix
    
    # Generate random community affiliation vector
    Ci = np.random.randint(1, num_communities + 1, size=num_nodes)  # Random integers representing community indices
    
    return W, Ci


def participation_coef_norm(W, Ci, n_iter=100, par_comp=0):
    """
    Normalized Participation Coefficient using randomizations
    
    Args:
    - W: binary and undirected connectivity matrix
    - Ci: community affiliation vector
    - n_iter (optional): number of matrix randomizations (default = 100)
    - par_comp (optional): 0 = don't compute matrix randomizations in a parallel loop (default = 0)
                           1 = compute matrix randomizations in a parallel loop
    
    Returns:
    - PC_norm: Normalized Participation Coefficient using randomizations
    - PC_residual: Residual Participation Coefficient from linear regression
    - PC: Original Participation Coefficient
    - between_mod_k: Between-module degree
    """
    n = len(W)  # number of vertices
    Ko = np.sum(W, axis=1)  
    Gc = np.dot((W != 0), np.diag(Ci))  # neighbor community affiliation

    Kc2 = np.zeros(n)
    within_mod_k = np.zeros(n)
    print("Shape of W:", W.shape)
    print("Shape of Gc:", Gc.shape)
    #print("Shape of (Gc == i)[:, np.newaxis]:", (Gc == i)[:, np.newaxis].shape)
    for i in range(1, int(np.max(Ci)) + 1):
        print("Shape of (Gc == i)[:, np.newaxis]:", (Gc == i)[:, np.newaxis].shape)
        Kc2 += np.sum(W * (Gc == i)[:, np.newaxis], axis=1) ** 2  # squared intra-modular degree
        within_mod_k[Ci == i] = np.sum(W[Ci == i][:, Ci == i], axis=1)  # within-module degree
        

    between_mod_k = Ko - within_mod_k  # [network-wide degree - within-module degree = between-module degree]
    PC = 1 - Kc2 / (Ko ** 2)  # calculate participation coefficient
    PC[Ko == 0] = 0  # PC = 0 for nodes with no (out)neighbors

    # Now over to Normalized Participation Coefficient
    Kc2_rnd = np.zeros((n, n_iter))  # initialize randomized intra-modular degree array

    if par_comp == 0:  # no parallel computing
        for ii in range(n_iter):  # number of randomizations
            if np.all(W == W.T):  # check whether network is undirected
                W_rnd = null_model_und_sign(W, 5)  # randomize each undirected network five times [ This is the function available in the fieldtrip package https://github.com/fieldtrip/fieldtrip/blob/master/external/bct/null_model_und_sign.m]
            else:
                W_rnd = randmio_dir(W, 5)  # randomize directed network five times

            Gc_rnd = np.dot((W_rnd != 0), np.diag(Ci))  # neighbor community affiliation
            Kc2_rnd_loop = np.zeros(n)  # initialize randomized intramodular degree vector - for current iteration only

            for iii in range(1, int(np.max(Ci)) + 1):  # estimate the squared difference between original and randomised intramodular degree
                Kc2_rnd_loop += (((np.sum(np.dot(W,(Gc == iii)), axis=1) / Ko) - (np.sum(np.dot(W_rnd, (Gc_rnd == iii)), axis=1) / Ko)) ** 2)
                

                #print("Shape of Gc == iii:", Gc_i.shape)
                #print("Shape of Gc_rnd == iii:", Gc_rnd_i.shape)
                Kc2_rnd_loop += (((np.sum(W * (Gc == iii[:, np.newaxis, np.newaxis]), axis=1) / Ko) - (np.sum(W_rnd * (Gc_rnd == iii[:, np.newaxis, np.newaxis]), axis=1) / Ko)) ** 2)
            Kc2_rnd[:, ii] = np.sqrt(0.5 * Kc2_rnd_loop)  # 0.5 * square root of intramodular degree between original and randomised network
    else:  # parallel computing
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for ii in range(n_iter):  # number of randomizations
                if np.all(W == W.T):  # check whether network is undirected
                    future = executor.submit(null_model_und_sign, W, 5)  # randomize each undirected network five times
                else:
                    future = executor.submit(randmio_dir, W, 5)  # randomize directed network five times
                futures.append(future)

            for ii, future in enumerate(futures):
                W_rnd = future.result()
                Gc_rnd = np.dot((W_rnd != 0), np.diag(Ci))  # neighbor community affiliation
                Kc2_rnd_loop = np.zeros(n)  # initialize randomized intramodular degree vector - for current iteration only

                for iii in range(1, int(np.max(Ci)) + 1):  # estimate the squared difference between original and randomised intramodular degree
                    Kc2_rnd_loop += (((np.sum(W * (Gc == iii), axis=1) / Ko) - (np.sum(W_rnd * (Gc_rnd == iii), axis=1) / Ko)) ** 2)
                    #Kc2_rnd_loop += (((np.sum(W * (Gc == iii[:, np.newaxis, np.newaxis]), axis=1) / Ko) - (np.sum(W_rnd * (Gc_rnd == iii[:, np.newaxis, np.newaxis]), axis=1) / Ko)) ** 2)

                Kc2_rnd[:, ii] = np.sqrt(0.5 * Kc2_rnd_loop)  # 0.5 * square root of intramodular degree between original and randomised network

    PC_norm = 1 - np.median(Kc2_rnd, axis=1)  # calculate normalized participation coefficient
    PC_norm[Ko == 0] = 0  # PC_norm = 0 for nodes with no (out)neighbors

    p = np.polyfit(np.sum(Ci == Ci, axis=1), PC, 1)  # linear regression
    yfit = np.polyval(p, np.sum(Ci == Ci, axis=1))  # best fit of regression
    PC_residual = PC - yfit  # residual participation coefficient
    PC_residual[Ko == 0] = 0  # PC_residual = 0 for nodes with no (out)neighbors

    return PC_norm, PC_residual, PC, between_mod_k

# Example usage:
num_nodes = 20  # Number of nodes
num_communities = 5  # Number of communities
W, Ci = generate_dummy_data(num_nodes, num_communities)



PC_norm, PC_residual, PC, between_mod_k = participation_coef_norm(W, Ci, n_iter=10)
