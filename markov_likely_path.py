import numpy as np
import random
import pickle
import re
from progress import ProgressBar
import sys

class Markov_model:
    def __init__(self,filename):
        dfile= filename.split('.')[0]+'.pkl'
        try:
            dump = self.loadfile(dfile)
            self.bag_of_word=dump['bag_of_word']
            self.bag_of_index = dump['bag_of_index']
            self.markov_matrix = np.array(dump['markov_matrix'])
        except OSError as e:
            self.bag_of_word={}
            self.bag_of_index = {}
            self.markov_matrix = np.array([[0]])
            index = 0
            try:
                with open(filename , 'r') as file:
                    print("log: this would show up if its a new file. A markov chain will be created and saved")
                    low = (' '.join(file.read().splitlines())).split(' ')
                    progress = ProgressBar(len(low)-1, fmt=ProgressBar.FULL)
                    for i in range(progress.total):
                        progress.current += 1
                        progress()
                        if self.bag_of_word.setdefault(low[i],index) == index:
                            self.bag_of_index[index]=low[i]
                            self.markov_matrix = np.pad(self.markov_matrix , [(0,self.max(index)),(0,self.max(index))] , mode='constant')
                            index+=1
                        if self.bag_of_word.setdefault(low[i+1],index) == index:
                            self.bag_of_index[index]=low[i+1]
                            self.markov_matrix = np.pad(self.markov_matrix , [(0,self.max(index)),(0,self.max(index))] , mode='constant')
                            index+=1
                        self.markov_matrix[self.bag_of_word[low[i]]][self.bag_of_word[low[i+1]]] +=1
                    progress.done()
                s = np.sum(self.markov_matrix , axis = 1)[: , np.newaxis]
                s[s==0]=1
                self.markov_matrix = self.markov_matrix / s
                self.markov_matrix[self.markov_matrix.shape[0]-1][0]=1
                dump={}
                dump['bag_of_word'] = self.bag_of_word
                dump['bag_of_index'] = self.bag_of_index
                dump['markov_matrix'] = self.markov_matrix
                self.savefile(dump ,dfile)
                del(dump)
                print("log:chain for ",filename," is created")
            except OSError as e:
                print("file not found !")
                exit()
    def savefile(self ,dump ,  filename):
        with open(filename , 'wb') as file:
            pickle.dump(dump , file , pickle.HIGHEST_PROTOCOL)
    def loadfile(self , filename):
        with open(filename , 'rb') as file:
            return pickle.load(file)

    def max(self,x):
        return int(x/x) if (x > 0) else 0

    def generate_biased_probability(self , len , seed=None):
        if(seed == None):
            seed = random.randint(0 , self.markov_matrix.shape[0]-1)
        string=""
        for i in range(len):
            string+=self.bag_of_index[seed]+" "
            outcoomes = list(range(self.markov_matrix.shape[0]))
            probab = self.markov_matrix[seed].tolist()
            seed = np.random.choice(outcoomes,p=probab)
        return string

    # def generate_max_likely_dynamically(self , len):
    #     '''
    #         biggest issue with this method is that it assumes a dynamic approach of finding
    #         the most likelyhood path, but since its a graph and movement is unrestricted
    #         the dynamic approach fails since most times its stuck in some loop of states
    #         e.g revelation, the Hindu is the Hindu is the Hindu is
    #         e.g do?" "You would be the Hindu is the Hindu is
    #         etc
    #         
    #     '''
    #     seed = random.randint(0 , self.markov_matrix.shape[0]-1)
    #     probab=1
    #     string=""
    #     for i in range(len):
    #         string+=self.bag_of_index[seed]+" "
    #         prev_seed = seed
    #         seed = np.argmax( self.markov_matrix[prev_seed] * probab)
    #         probab = self.markov_matrix[prev_seed][seed] * probab
    #     return string

    def create_context_graph(self ,seed, deapth , state_probab):
        '''
            Creates a spanning tree in deapth first order since the deapth is restricted
            seed is the root node , deapth is the deapth of search to create the sub graph
            state_probab is the probability above which the states muct must be observed

            state_probab is highly dependent on corpus text 0.0 will include all the letters and create
            a meaning less graph , 0.1 - 0.05 gives you meaning full graph size
        '''
        edge_list = set()
        vertex_list = set()
        vertex_list.add(seed)
        children= np.argwhere(self.markov_matrix[seed] >= state_probab ).flatten()
        if children.shape[0] != 0 and deapth > 0:
            for i in range(children.shape[0]):
                edge_list.add((seed,children[i]))
                vertex_list.add(children[i])
                e,v = self.create_context_graph(children[i] , deapth-1 , state_probab)
                if e != None:
                    edge_list = edge_list.union(e)
                    vertex_list = vertex_list.union(v)
            return (edge_list , vertex_list)
        return (None , None)

    def create_context_tree(self ,seed, depth , probab):
        '''
            creates a minimum spanning tree on the markov model

        '''
        e , v = self.create_context_graph(seed, depth , probab)
        if e == None:
            return None
        e = sorted(e , key=lambda x:-np.log(self.markov_matrix[x[0]][x[1]]))
        mst_vertex=set()
        mst_edge=set()
        mst_vertex.add(seed)
        tree = {
            seed:{'parent':-1 , 'child':[]},
        }
        while mst_vertex != v:
            smallest=np.inf
            ed=()
            for edge in e:
                if(edge[0] in mst_vertex and edge[1] in v.difference(mst_vertex)):
                    if -np.log(self.markov_matrix[edge[0]][edge[1]]) < smallest:
                        smallest = -np.log(m.markov_matrix[edge[0]][edge[1]])
                        ed = edge
            mst_edge.add(ed)
            tree[ed[0]]['child'].append(ed[1])
            mst_vertex.add(ed[1])
            tree[ed[1]]={'parent':ed[0],'child':[]}
        return tree
    
    def context_likely_sequence(self,seed,depth,probab):
        tree = self.create_context_tree(seed,depth,probab)
        if tree == None:
            return None
        self.sequence = []
        self.accum=0
        self.walk_tree([] , seed , 0 , tree , 0)
        return self.sequence


    def walk_tree(self , sequence , node ,dist, tree , path_sum):
        path_sum+=dist
        sequence.append(node)
        if(self.accum < path_sum):
            self.accum = path_sum
            self.sequence = sequence
        for n in tree[node]['child']:
            self.walk_tree(sequence[:],n ,-np.log(self.markov_matrix[node][n]), tree , path_sum)
        
    def generate_random_likely_sequence(self,iterations,seed=None , depth=3,probab=0.02):
        if seed == None:
            seed = random.randint(0 , self.markov_matrix.shape[0]-1)
        sequence=[]    
        sequence = self.context_likely_sequence(seed,depth,probab)
        if sequence == None or sequence == [] or len(sequence) == 1:
            return "markov chain encountered a 0 probability of state change, highly unlikely but can happen !!"
        for i in range(iterations):
            seq = self.context_likely_sequence(sequence[-1],depth,probab)
            if seq == None:
                break
            sequence+=seq[1:]
        string=""
        for i in sequence:
            string+=self.bag_of_index[i]+" "
        return string
if len(sys.argv) < 2:
    print("err !! give file name")
    exit()
text=sys.argv[1]            
m = Markov_model(text)

print("Likely hood sentences 1: " , m.generate_random_likely_sequence(3 ,depth=3 , probab=0.03 ))
print("Likely hood sentences 2: " , m.generate_random_likely_sequence(3 ,depth=5 , probab=0.04 ))
print("Random sentence with biased probability: " ,m.generate_biased_probability(30 ))




