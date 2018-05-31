# Markov-Chain-Likely-Text-Generator-
This is a markov chain implementation that does not generates text on random. It finds the most likely path after creating a tree from subgraph of the entire fully connected graph

What this project does is reads of an txt text and creates a markov chain model out of it

1.  then run a single point longest path algorithm on it for probability of next word getting  
    decreased at each node.

2.  run a stochastic decision tree creator by going through PRIMS method of spanning   
    stochastic tree:http://users.iems.northwestern.edu/~hazen/StochasticTreeIntro.doc  
    
    the graph in markov models are stochastic in nature, so in space of optimization problems
    this would be np hard if we are to find maximum spanning tree or forest of the entire graph.  
    So what we do is we generate sub graphs of sepcified deapths i.e when the subgraph is created  
    the search is limited to d level and then terminated.  
    Next we need to find a most likely path in this directed graph. Since the graph is directed  
    much of our problem is solved.  
    one likely solution for this purpose was the viterby algorithm. 

3.  We use the logarithmic value of the probabiliies to work out the minimum spanning tree
    Now What we want for any markov subgraph is to find a spanning tree in it that will have  
    minimum negative logarithmic value of the edges. Since edges are in range of 0 to 1  
    hence we take logarithms
        we need to   
                    max( p1 * p2 * p3 * ...)  
                    problem is proablities when multiplied are can give fluctuating values    
                    as multiplication in fraction can raise and decrease result  
                    i.e 0.9 * 0.9 decreases the result from its input  
                    so we take log  
                    min -log(p1 * p2 * p3 * p4 * p5 ...)  
                    min -log(p1) + -log(p2) + -log(p3) ....  
                    which is no more a stochastic spanning tree problem but a simple spanning tree problem  
    After this we find the spanning tree and do a deapth first search for the highest sum of logarithms   
    to find the most likely output  given a seed value
    link for probability idea:https://pdfs.semanticscholar.org/6797/03bb217b5edef12017354ed1dc68476a7ce6.pdf  

4. Finally we can iterate and keep generating most likely paths using the end of the each new sequence  

### Why do this  
The idea is to get more likely sentences . To introduce determinsim in stochastic generation process  
It should allow us to create context specific sentences from the ground truth i.e the corpus  
but also have its own unique random sentences.

### How to use

```python

python markov_likely_path.py hamlet.txt

```


```shell

    log: this would show up if its a new file. A markov chain will be created and saved
    [========================================] 33475/33475 (100%)     0 to go
    log:chain for  hamlet.txt  is created
    Likely hood sentences 1:  Esile, eate a
    Likely hood sentences 2:  try, Directly seasons him to be
    Random sentence with biased probability:  You cannot be so. We will I cannot be, Till that Season comes it?    Ham. Indeed, indeed  Hor. Heauen and Religious feare it, you
    me to
```

```shell

python markov*.py hamlet.txt

Likely hood sentences 1:  Colours, and the
Likely hood sentences 2:  bow them  Ham. I will speake no more then it selfe in my Lord, if not, Be wary eye looke where 'tis so, please him. This must tell vs where 'tis so, When thou hast strooke
Random sentence with biased probability:  Houres     Ham. I shall not  Ham. Neuer alone my Lord, the crowing of this Pearle is that? Being a paire of England   King.

```
