# to install gurobipy: 
# cd /shared/why16gzl/Downloads/gurobi811/linux64
# python setup.py install

from gurobipy import *
import numpy as np
from collections import defaultdict 
import math
class gurobi_opt:
    def __init__(self, edges):
        self.why_score = why_score = self.convert_to_score(edges)
        self.model = Model('lp')
        self.x = self.model.addVars(why_score.shape[0], why_score.shape[1], why_score.shape[2], lb=0.0, ub=1.0, obj=why_score, vtype=GRB.INTEGER, name="x")
        
        # before OR after
        self.prob_constrs = self.model.addConstrs((self.sum_prob(i, j) == 1 \
                                                   for i in range(why_score.shape[0]) \
                                                   for j in range(why_score.shape[0]) \
                                                   if i != j), name='prob_constrs')
        
        # (1,0) is before => (0,1) is after
        self.sym_constrs = self.model.addConstrs((self.x[i, j, 0] == self.x[j, i, 1] \
                                                  for i in range(why_score.shape[0]) \
                                                  for j in range(why_score.shape[0]) \
                                                  if i != j), name='sym_constrs')
        
        # (0,1) is before; (1,2) is before => (0,2) is before
        self.trans_constrs_0 = self.model.addConstrs((self.x[i, j, 0] + self.x[j, k, 0] - self.x[i, k, 0] <= 1 \
                                                    for i in range(why_score.shape[0]) \
                                                    for j in range(why_score.shape[0]) \
                                                    for k in range(why_score.shape[0]) \
                                                    if i != j and j != k and k != i), name='trans_constrs_0')
        
        # (0,1) is after; (1,2) is after => (0,2) is after
        self.trans_constrs_1 = self.model.addConstrs((self.x[i, j, 1] + self.x[j, k, 1] - self.x[i, k, 1] <= 1 \
                                                    for i in range(why_score.shape[0]) \
                                                    for j in range(why_score.shape[0]) \
                                                    for k in range(why_score.shape[0]) \
                                                    if i != j and j != k and k != i), name='trans_constrs_1')
        
        self.model.update()
        self.sum_score = 0.0
        for i in range(self.why_score.shape[0]):
            for j in range(self.why_score.shape[1]):
                for k in range(self.why_score.shape[2]):
                    if self.why_score[i][j][k] != 0:
                        self.sum_score += self.x[i, j, k] * self.why_score[i][j][k]
        self.obj = self.sum_score - self.x.sum()
        self.model.setObjective(self.obj, GRB.MAXIMIZE) # maximize profit
        self.model.optimize()
        
    def __call__(self):
        for v in self.model.getVars():
            print('%s %g' % (v.varName, v.x))
        return self.model.getVars()
    
    def convert_to_score(self, edges):
        num_event = math.ceil(math.sqrt(len(edges.keys()) * 2))
        why_score = np.zeros((num_event, num_event, 2))
        for k, v in edges.items():
            why_score[int(k.split(',')[0])][int(k.split(',')[1])][0] = v
            why_score[int(k.split(',')[0])][int(k.split(',')[1])][1] = 1 - v
        return why_score  
    
    def sum_prob(self, i, j):
        sum_prob = 0.0
        for k in range(self.why_score.shape[2]):
            sum_prob += self.x[i, j, k]
        return sum_prob
    
    def gurobi_output(self):
        output = np.zeros_like(self.why_score)
        for i in range(output.shape[0]):
            for j in range(output.shape[1]):
                for k in range(output.shape[2]):
                    output[i][j][k] = self.x[i, j, k].X
        return output

#Class to represent a graph 
class Graph: 
    def __init__(self,vertices): 
        self.graph = defaultdict(list) #dictionary containing adjacency List 
        self.V = vertices #No. of vertices 
  
    # function to add an edge to graph 
    def addEdge(self,u,v): 
        self.graph[u].append(v) 
  
    # A recursive function used by topologicalSort 
    def topologicalSortUtil(self,v,visited,stack): 
  
        # Mark the current node as visited. 
        visited[v] = True
  
        # Recur for all the vertices adjacent to this vertex 
        for i in self.graph[v]: 
            if visited[i] == False: 
                self.topologicalSortUtil(i,visited,stack) 
  
        # Push current vertex to stack which stores result 
        stack.insert(0,v) 
  
    # The function to do Topological Sort. It uses recursive  
    # topologicalSortUtil() 
    def topologicalSort(self): 
        # Mark all the vertices as not visited 
        visited = [False]*self.V 
        stack =[] 
  
        # Call the recursive helper function to store Topological 
        # Sort starting from all vertices one by one 
        for i in range(self.V): 
            if visited[i] == False: 
                self.topologicalSortUtil(i,visited,stack) 
  
        # Print contents of stack 
        return stack
