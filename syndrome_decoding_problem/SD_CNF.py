from pysat.card import CardEnc
from pysat.pb import PBEnc
from pysat.formula import CNF
from utils import *

def build_CNF1(n, w, H_transpose, s_transpose, cc_encoding, pb_encoding):
    """
    Build the CNF1 formula for the syndrome decoding problem.

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        H_transpose (list of str): The transposed parity-check matrix.
        s_transpose (str): The syndrome vector.
        cc_encoding (str): Cardinality constraint encoding to use.
        pb_encoding (str):  Pseudo-Boolean constraint encoding to use.

    Returns:
        cnf (CNF): The CNF formula representing the problem.
    """
    
    m = len(s_transpose)  # Number of equations
    cnf = CNF()

    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    
    # Build sets V and K
    V , K = build_var_sets(H_transpose, s_transpose, n, w)
    
    # Introduce auxiliary variables x_{i,v} 
    top_id = n  # Highest variable index so far
    x_vars_dict = {}  #  Mapping (i, v) to the variable x_{i,v}
    for i in range(m):
        x_vars = []
        for v in K[i]:
            top_id += 1  # Allocate a new variable
            x_vars_dict[(i, v)] = top_id
            x_vars.append(top_id)

        # For each equation, enforce that exactly one auxiliary variable x_{i,v} is set to true
        if x_vars:
            res = CardEnc.equals(lits=x_vars, bound=1, top_id=top_id, encoding=cc_encoding)
            cnf.extend(res.clauses)
            top_id = res.nv # Update top_id to reflect newly used variables
        
    
    # Encode the pseudo-Boolean equality constraints for each equation E_i
    for i, V_i in enumerate(V):
        e_vars_i = V_i  # Variables involved in equation E_i
        e_weights = [1] * len(e_vars_i) # All e_j have coefficient 1
        
        # Construct literals and weights for auxiliary x_{i,v} variables
        x_lits = []
        x_weights = []
        for v in K[i]:
            if v != 0:
                x = x_vars_dict[(i, v)]
                x_lits.append(-x)   
                x_weights.append(v)
        
        # Right-hand side is the sum of all possible values v in K_{E_i}
        rhs = sum(K[i])
        
        lits = e_vars_i + x_lits
        weights = e_weights + x_weights
        
        # Encode the PB equality constraint
        res_eq = PBEnc.equals(lits=lits, weights=weights, bound=rhs, top_id=top_id, encoding=pb_encoding)
        cnf.extend(res_eq.clauses)
        top_id = res_eq.nv 
    
    # Encode the constraint on the total Hamming weight of e
    res_atmost = CardEnc.atmost(lits=e_vars, bound=w, top_id=top_id, encoding=cc_encoding)
    cnf.extend(res_atmost.clauses)
    
    return cnf



def build_CNF2(n, w, H_transpose, s_transpose, cc_encoding, pb_encoding):
    """
    Build the CNF2 formula for the syndrome decoding problem.

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        H_transpose (list of str): The transposed parity-check matrix.
        s_transpose (str): The syndrome vector.
        cc_encoding (str): Cardinality constraint encoding to use.
        pb_encoding (str):  Pseudo-Boolean constraint encoding to use.

    Returns:
        cnf (CNF): The CNF formula representing the problem.
    """

    m = len(s_transpose)  # Number of equations
    cnf = CNF()
    
    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    
    # Build sets V and K
    V , K = build_var_sets(H_transpose, s_transpose, n, w)
    
    # Introduce auxiliary variables x_{i,v} 
    top_id = n  # Highest variable index so far
    x_vars_dict = {}  #  Mapping (i, v) to the variable x_{i,v}
    for i in range(m):
        for v in K[i]:
            top_id += 1  
            x_vars_dict[(i, v)] = top_id  

    
    for i, V_i in enumerate(V):
        e_vars_i = V_i  # Variables involved in equation E_i
        e_weights = [1] * len(e_vars_i) # All e_j have coefficient 1
        
        # Handle auxiliary variables x_{i,v} for v ∈ K_{E_i} \ {0,1}
        x_lits = []
        x_weights = []
        for v in K[i]:
            if v not in {0, 1}:
                x = x_vars_dict[(i, v)]
                x_lits.append(-x) # Use negated x_{i,v}
                x_weights.append(2) # Weight 2 for each negated x_{i,v} 
        
        # Right-hand side is the maximum value in K_{E_i}
        rhs = max(K[i])
        
        # Combine literals and weights for PB constraint
        lits = e_vars_i + x_lits
        weights = e_weights + x_weights
        
        # Encode the PB equality constraint
        res_eq = PBEnc.equals(lits=lits, weights=weights, bound=rhs, top_id=top_id, encoding=pb_encoding)
        cnf.extend(res_eq.clauses)
        top_id = res_eq.nv

    # Unary constraint: x_{i,v} = 1 if sum(e_j for j in V_{E_i}) == v
    for i in range(m):
        for v in K[i]:
            if v not in {0, 1, 2, 3}:
                if (i, v-2) in x_vars_dict:
                    cnf.append([-x_vars_dict[(i, v)], x_vars_dict[(i, v-2)]])
    
    # Encode the constraint on the total Hamming weight of e
    res_atmost = CardEnc.atmost(lits=e_vars, bound=w, top_id=top_id, encoding=cc_encoding)
    cnf.extend(res_atmost.clauses)
    
    return cnf