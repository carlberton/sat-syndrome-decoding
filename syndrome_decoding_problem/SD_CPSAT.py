import os
import time
import csv
import argparse
from ortools.sat.python import cp_model
from utils import *

def build_and_solve_CP1(n, w, H_transpose, s_transpose, timeout=10800):
    """
    Model and solve the syndrome decoding problem using CP-SAT (CNF1-style encoding).

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        H_transpose (list of str): The transposed parity-check matrix.
        s_transpose (str): The syndrome vector.
        timeout (int): Time limit in seconds.
    
    Returns:
        status_str (str): 'sat', 'unsat', 'unknown', or 'model_invalid'.
        res_time (str): Resolution time in seconds.
        solution (str or None): Binary solution string for e_j variables if satisfiable.
    """

    model = cp_model.CpModel()
    
    # Variables e_j numbered from 1 to n
    e_vars = [model.NewBoolVar(f"e_{j}") for j in range(1, n+1)]
    
    # Build sets V and K
    V, K = build_var_sets(H_transpose, s_transpose, n, w)
    if any(not K_i for K_i in K):
        return "unsat", "0.00000", None
    
    # For each parity-check equation E_i:
    for i, V_i in enumerate(V):
        
        # Define auxiliary variables x_{i,v} and xbar_{i,v}
        x_vars = {}   
        xbar_vars = {}
        for v in K[i]:
            x = model.NewBoolVar(f"x_{i}_{v}")
            xbar = model.NewBoolVar(f"xbar_{i}_{v}")
            
            # Enforce: x + xbar = 1 
            model.Add(x + xbar == 1)
            x_vars[v] = x
            xbar_vars[v] = xbar

        # Exactly one x_{i,v} is set to 1
        model.Add(sum(x_vars.values()) == 1)
        

        # Build sum constraint
        rhs = sum(K[i]) # Right-hand side is the sum of all possible values v in K_{E_i}
        terms = []
        # Add e_j variables (weight 1)
        for idx in V_i:
            terms.append(e_vars[idx - 1])

        # Add auxiliary terms: v * xbar_{i,v}
        for v, xbar in xbar_vars.items():
            if v != 0 :
                terms.append(xbar * v)
        
        model.Add(sum(terms) == rhs)

    # Add constraint on the total Hamming weight of e
    model.Add(sum(e_vars) <= w)

    # Solve the model using CP-SAT
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = timeout # default : 3-hour timeout

    start = time.perf_counter()
    status = solver.Solve(model)
    res_time = time.perf_counter() - start
    res_time = f"{res_time:.5f}"

    # Extract solution if feasible/optimal
    solution = None
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [solver.Value(e_j) for e_j in e_vars]
        solution = ''.join(map(str, solution))
        status_str = 'sat'
    elif status == cp_model.INFEASIBLE:
        status_str = 'unsat'
    elif status == cp_model.MODEL_INVALID:
        status_str = 'model_invalid'
    else:
        status_str = 'unknown'

    return status_str, res_time, solution


def build_and_solve_CP2(n, w, H_transpose, s_transpose, timeout=10800):
    """
    Model and solve the syndrome decoding problem using CP-SAT (CNF2-style encoding).

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        H_transpose (list of str): The transposed parity-check matrix.
        s_transpose (str): The syndrome vector.
        timeout (int): Time limit in seconds.
    
    Returns:
        status_str (str): 'sat', 'unsat', 'unknown', or 'model_invalid'.
        res_time (str): Resolution time in seconds.
        solution (str or None): Binary solution string for e_j variables if satisfiable.
    """

    model = cp_model.CpModel()
    
    # Variables e_j numbered from 1 to n
    e_vars = [model.NewBoolVar(f"e_{j}") for j in range(1, n+1)]
    
    # Build sets V and K
    V, K = build_var_sets(H_transpose, s_transpose, n, w)
    if any(not K_i for K_i in K):
        return "unsat", "0.00000", None
    
    # For each parity-check equation E_i:
    for i, V_i in enumerate(V):
        
        # Define auxiliary variables x_{i,v} and xbar_{i,v}
        x_vars = {}    
        xbar_vars = {} 
        for v in K[i]:
            x = model.NewBoolVar(f"x_{i}_{v}")
            xbar = model.NewBoolVar(f"xbar_{i}_{v}")
            
            # Enforce: x + xbar = 1 
            model.Add(x + xbar == 1)
            x_vars[v] = x
            xbar_vars[v] = xbar
        
        # Build sum constraint
        rhs = max(K[i])  # Right-hand side is the maximum value in K_{E_i}
        terms = []
        # Add e_j variables (weight 1)
        for idx in V_i:
            terms.append(e_vars[idx-1])

        # Add auxiliary terms: 2 * xbar_{i,v}
        for v, xbar in xbar_vars.items():
            if v not in {0,1} :
                terms.append(xbar * 2)
        
        # Enforce the constraint: sum(e_j) + sum(2 * xbar_{i,v}) == max(K[i])
        model.Add(sum(terms) == rhs)
        
        # Unary ordering: x_{i,v} implies x_{i,v-2}.
        for v in K[i]:
            if v not in {0,1,2,3} and (v-2) in x_vars:
                model.AddBoolOr([xbar_vars[v], x_vars[v-2]])

    # Add constraint on the total Hamming weight of e
    model.Add(sum(e_vars) <= w)
    
    # Solve the model using CP-SAT
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = timeout # default : 3-hour timeout

    start = time.perf_counter()
    status = solver.Solve(model)
    res_time = time.perf_counter() - start
    res_time = f"{res_time:.5f}"

    # Extract solution if feasible/optimal
    solution = None
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [solver.Value(e_j) for e_j in e_vars]
        solution = ''.join(map(str, solution))
        status_str = 'sat'
    elif status == cp_model.INFEASIBLE:
        status_str = 'unsat'
    elif status == cp_model.MODEL_INVALID:
        status_str = 'model_invalid'
    else:
        status_str = 'unknown'

    return status_str, res_time, solution



def process_file(file_path, solve_function, timeout=10800):
    """
    Process a single input file and solve the syndrome decoding problem.

    Args:
        file_path (str): Path to the input file containing problem parameters.
        solve_function (function): Function to solve the problem (build_and_solve_CP1 or build_and_solve_CP2).
        timeout (int): Time limit in seconds.
    
    Returns:
        tuple: A tuple containing:
            - file (str): The name of the input file.
            - status (str): 'sat', 'unsat', 'unknown', 'model_invalid', or 'invalid_solution'.
            - res_time (str): Resolution time in seconds.
            - sol (str or None): Binary solution string for e_j variables if satisfiable, or an error message.
    """

    # Parse the input file to extract problem parameters
    n, _, w, H_transpose, s_transpose = parse_input_file(file_path)
    
    # Solve the problem using the specified solving function 
    status, res_time, sol = solve_function(n, w, H_transpose, s_transpose, timeout=timeout)
    file = os.path.basename(file_path)

    # If the solution is satisfiable, verify its validity
    if status == 'sat' and sol is not None:
        is_valid = verify_sol(file_path, sol)
        if is_valid: 
            return file, status, res_time, sol
        else:
            return file, 'invalid_solution', res_time, sol
    else:
        return file, status, res_time, "No solution"



def main():
    # Set up argument parser for command-line options
    parser = argparse.ArgumentParser(description="CPSAT solver for syndrome decoding.")
    parser.add_argument('-m', '--method', choices=['CNF1', 'CNF2'], required=True, help="Resolution method to use (CNF1 or CNF2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Path to an input file')
    group.add_argument('-d', '--dir', help='Path to a directory to process')
    parser.add_argument("--timeout", type=int, default=10800,
                        help="Time limit per instance in seconds (default: 10800)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be strictly positive")

    # Select the solving function based on the chosen method
    solve_function = build_and_solve_CP1 if args.method == 'CNF1' else build_and_solve_CP2

    if args.file:
        # Process a single file
        file, status, res_time, sol = process_file(args.file, solve_function, args.timeout)
        directory = os.path.dirname(args.file)
        csv_filepath = os.path.join(directory, f"CPSAT_{args.method}_{os.path.splitext(file)[0]}.csv")
        with open(csv_filepath, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["File", "Result", "Time (s)", "Solution"])
            csv_writer.writerow([file, status, res_time, sol])
            csvfile.flush()
    else:
        # Process all files in a directory
        csv_filepath = os.path.join(args.dir, f"CPSAT_{args.method}.csv")
        os.makedirs(args.dir, exist_ok=True)  
        with open(csv_filepath, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["File", "Result", "Time (s)", "Solution"])
            csvfile.flush()

            # Filter and sort files in the directory
            entries = [
                entry for entry in os.listdir(args.dir)
                if os.path.isfile(os.path.join(args.dir, entry)) and '.' not in os.path.basename(entry)
            ]
            entries.sort(key=extract_SD_n)

            # Process each file in the directory
            for entry in entries:
                path = os.path.join(args.dir, entry)
                print(f"\n--- Processing {path} ---")
                file, status, res_time, sol = process_file(path, solve_function, args.timeout)
                csv_writer.writerow([file, status, res_time, sol])
                csvfile.flush()

    print(f"Results written to {csv_filepath}")



if __name__ == "__main__":
    main()