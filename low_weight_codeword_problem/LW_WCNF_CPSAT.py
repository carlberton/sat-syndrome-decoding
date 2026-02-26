import argparse
import csv
import time
from ortools.sat.python import cp_model
from utils import *

def build_and_solve_CP1(n, H_transpose):
    model = cp_model.CpModel()
    
    # Variables e_j 
    e_vars = [model.NewBoolVar(f"e_{j}") for j in range(1, n+1)]
    
    # Construction of sets V_i
    V = []
    for i, row in enumerate(H_transpose):
        V_i = [i + 1]
        for j, val in enumerate(row):
            if val == '1':
                V_i.append(j + n//2 + 1)
        V.append(V_i)
    
    # For each equation E_i
    for i, V_i in enumerate(V):
        # calculation of K_i
        max_val = len(V_i)
        K_i = [v for v in range(max_val+1) if v % 2 == 0]
        
        
        x_vars = {}     # x_{i,v}
        xbar_vars = {}  # \bar x_{i,v}
        if len(K_i) > 0:
            for v in K_i:
                x = model.NewBoolVar(f"x_{i}_{v}")
                xbar = model.NewBoolVar(f"xbar_{i}_{v}")
                # x + xbar = 1  <=>  xbar = 1 − x
                model.Add(x + xbar == 1)
                x_vars[v] = x
                xbar_vars[v] = xbar
            # exactly one of the x_{i,v} equals 1
            model.Add(sum(x_vars.values()) == 1)
        
        # sum e_j + sum v* xbar_{i,v} == sum(K_i)
        rhs = sum(K_i)
        terms = []
        # sum of e_j
        for idx in V_i:
            terms.append(e_vars[idx-1])
        # sum of v * xbar_{i,v}
        for v, xbar in xbar_vars.items():
            if v != 0 :
                terms.append(xbar * v)
        
        model.Add(sum(terms) == rhs)

    model.Minimize(sum(e_vars))
    model.Add(sum(e_vars) > 0)

    # Resolution
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10800

    start = time.time()
    status = solver.Solve(model)
    res_time = time.time() - start
    res_time = f"{res_time:.5f}"

    solution = None
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [solver.Value(e_j) for e_j in e_vars]
        solution = ''.join(map(str, solution))
        status_str = 'sat'
    else:
        status_str = 'unsat' if status == cp_model.INFEASIBLE else 'timeout'

    return status_str, res_time, solution

def build_and_solve_CP2(n, H_transpose):
    model = cp_model.CpModel()
    
    e_vars = [model.NewBoolVar(f"e_{j}") for j in range(1, n+1)]
    
    # Construction of V_i
    V = []
    for i, row in enumerate(H_transpose):
        V_i = [i+1] + [j + n//2 + 1 for j, val in enumerate(row) if val == '1']
        V.append(V_i)
    
    # For each equation i
    for i, V_i in enumerate(V):
        # Calculation of K_i
        max_val = len(V_i)
        K_i = [v for v in range(max_val+1) if v % 2 == 0]
        
        x_vars = {}     # x_{i,v}
        xbar_vars = {}  # \bar x_{i,v}
        if len(K_i) > 0:
            for v in K_i:
                x = model.NewBoolVar(f"x_{i}_{v}")
                xbar = model.NewBoolVar(f"xbar_{i}_{v}")
                # x + xbar = 1  <=>  xbar = 1 − x
                model.Add(x + xbar == 1)
                x_vars[v] = x
                xbar_vars[v] = xbar
        
        # sum e_j + sum 2* xbar_{i,v} == max(K_i)
        rhs = max(K_i)
        terms = []
        # sum of e_j
        for idx in V_i:
            terms.append(e_vars[idx-1])
        # sum of v * xbar_{i,v}
        for v, xbar in xbar_vars.items():
            if v not in {0,1} :
                terms.append(xbar * 2)
        
        model.Add(sum(terms) == rhs)
        
        for v in K_i:
            if v not in {0,1,2,3} and (v-2) in x_vars:
                # AddBoolOr([¬x_{i,v}, x_{i,v-2}])
                model.AddBoolOr([xbar_vars[v], x_vars[v-2]])

    model.Minimize(sum(e_vars))
    model.Add(sum(e_vars) > 0)
    
    # Resolution
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10800

    start = time.time()
    status = solver.Solve(model)
    res_time = time.time() - start
    res_time = f"{res_time:.5f}"

    solution = None
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        solution = [solver.Value(e_j) for e_j in e_vars]
        solution = ''.join(map(str, solution))
        status_str = 'sat'
    else:
        status_str = 'unsat' if status == cp_model.INFEASIBLE else 'timeout'

    return status_str, res_time, solution


def process_file(file_path, solve_function):
    n, seed, H_transpose = parse_input_file(file_path)
    
    # Solve the problem with CP-SAT
    status, res_time, sol = solve_function(n, H_transpose)
    file = os.path.basename(file_path)

    if status == 'sat' and sol is not None:
        is_valid = verify_sol(file_path, sol)
        if is_valid: 
            return file, status, res_time, sol
        else:
            return file, status, res_time, "Invalid solution"
    else:
        return file, status, res_time, "No solution"
    

def main():
    parser = argparse.ArgumentParser(description="CPSat solver for the low-weight codeword problem.")
    parser.add_argument('-m', '--method', choices=['CNF1', 'CNF2'], required=True, help="Resolution method to use (CNF1 or CNF2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Path to an input file')
    group.add_argument('-d', '--dir', help='Path to a file to be processed')
    args = parser.parse_args()

    # Select the solving function based on the chosen method
    solve_function = build_and_solve_CP1 if args.method == 'CNF1' else build_and_solve_CP2

    if args.file:
        file, status, res_time, sol = process_file(args.file,solve_function)
        directory = os.path.dirname(args.file)
        csv_filepath = os.path.join(directory, f"CPSAT_W{args.method}_{os.path.splitext(file)[0]}.csv")
        with open(csv_filepath, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["File", "Result", "Time (s)", "Solution"])
            csv_writer.writerow([file, status, res_time, sol])
            csvfile.flush()
    else:
        csv_filepath = os.path.join(args.dir, f"CPSAT_W{args.method}.csv")
        os.makedirs(args.dir, exist_ok=True)  
        with open(csv_filepath, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["File", "Result", "Time (s)", "Solution"])
            csvfile.flush()

            entries = [
                entry for entry in os.listdir(args.dir)
                if os.path.isfile(os.path.join(args.dir, entry)) and '.' not in os.path.basename(entry)
            ]
            entries.sort(key=extract_n)

            for entry in entries:
                path = os.path.join(args.dir, entry)
                print(f"\n--- Traitement de {path} ---")
                file, status, res_time, sol = process_file(path,solve_function)
                csv_writer.writerow([file, status, res_time, sol])
                csvfile.flush()

    print(f"Résultats écrits dans {csv_filepath}")

if __name__ == "__main__":
    main()