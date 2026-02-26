from pysat.card import CardEnc
from pysat.pb import PBEnc
from pysat.formula import WCNF
from utils import *

def build_WCNF1(n, H_transpose, cc_encoding, pb_encoding):
    
    m = n // 2  # Number of equations
    cnf = WCNF()
    
    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    
    # Construction of the V_i sets line by line
    V = []
    for i, row in enumerate(H_transpose):
        V_i = [i + 1]  # Adding identity
        for j, val in enumerate(row):
            if val == '1':
                V_i.append(j + int(n / 2) + 1) 
        V.append(V_i)
    
    # For each equation E_i, define the set K_{E_i}
    K = []
    for i, V_i in enumerate(V):
        max_val = len(V_i)
        K_i = [j for j in range(max_val + 1) if j % 2 == 0]
        K.append(K_i)
    
    # Introduce the variables x_{i,v}
    top_id = n  
    x_vars_dict = {}  
    for i in range(m):
        x_vars = []
        for v in K[i]:
            top_id += 1  # Need a new variable
            x_vars_dict[(i, v)] = top_id
            x_vars.append(top_id)
        if x_vars:
            res = CardEnc.equals(lits=x_vars, bound=1, top_id=top_id, encoding=cc_encoding)
            cnf.extend(res.clauses)
            top_id = res.nv
        
    
    # Encoding of the pseudo-Boolean constraint
    for i, V_i in enumerate(V):
        
        e_vars_i = V_i  # variables e_j of equation E_i
        # Each e_j has a coefficient of 1 (to make a list)
        e_weights = [1] * len(e_vars_i)
        
        # Construct the literals and their weights for the variables x_{i,v}
        x_lits = []
        x_weights = []
        for v in K[i]:
            if v != 0:
                x = x_vars_dict[(i, v)]
                x_lits.append(-x)   
                x_weights.append(v)
        
        # Sum of the values ​​of K_{E_i}
        rhs = sum(K[i])
        
        lits = e_vars_i + x_lits
        weights = e_weights + x_weights
        
        # Pseudo-Boolean encoding with PBEnc.equals
        res_eq = PBEnc.equals(lits=lits, weights=weights, bound=rhs, top_id=top_id, encoding=pb_encoding)
        cnf.extend(res_eq.clauses)
        top_id = res_eq.nv 

    # At least one variable must be true
    cnf.append([i for i in range(1, n + 1)])

    # Soft clauses 
    for i in range(1, n + 1):
        cnf.append([-i], weight=1)
    
    return cnf


def build_WCNF2(n, H_transpose, pb_encoding):

    m = n // 2  # Number of equations
    cnf = WCNF()
    
    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    
    # Construction of the V_i sets line by line
    V = []
    for i, row in enumerate(H_transpose):
        V_i = [i + 1]  # Adding identity
        for j, val in enumerate(row):
            if val == '1':
                V_i.append(j + int(n / 2) + 1) 
        V.append(V_i)

    
    # For each equation E_i, define the set K_{E_i}
    K = []
    for i, V_i in enumerate(V):
        max_val = len(V_i)
        K_i = [j for j in range(max_val + 1) if j % 2 == 0]
        K.append(K_i)
    
    # Introduce the variables x_{i,v} for all v \in K_{E_i}
    top_id = n 
    x_vars_dict = {}  
    for i in range(m):
        for v in K[i]:
            top_id += 1  
            x_vars_dict[(i, v)] = top_id  

    # Encoding of the pseudo-Boolean constraint
    for i, V_i in enumerate(V):
        # Each e_j has a weight of 1
        e_vars_i = V_i
        e_weights = [1] * len(e_vars_i)
        
        # Section on the variables x_{i,v} for v \in K_{E_i} \ {0,1}
        x_lits = []
        x_weights = []
        for v in K[i]:
            if v not in {0, 1}:
                x = x_vars_dict[(i, v)]
                x_lits.append(-x)
                x_weights.append(2)
        
        # The right bound is the maximum of the elements of K_{E_i}
        rhs = max(K[i])
        
        # Combine literals and weights
        lits = e_vars_i + x_lits
        weights = e_weights + x_weights
        
        # Encoding with PBEnc.equals
        res_eq = PBEnc.equals(lits=lits, weights=weights, bound=rhs, top_id=top_id, encoding=pb_encoding)
        cnf.extend(res_eq.clauses)
        top_id = res_eq.nv

    for i in range(m):
        for v in K[i]:
            if v not in {0, 1, 2, 3}:
                if (i, v-2) in x_vars_dict:
                    cnf.append([-x_vars_dict[(i, v)], x_vars_dict[(i, v-2)]])

    # At least one variable must be true
    cnf.append([i for i in range(1, n + 1)])

    # Soft clauses
    for i in range(1, n + 1):
        cnf.append([-i], weight=1)
    
    return cnf