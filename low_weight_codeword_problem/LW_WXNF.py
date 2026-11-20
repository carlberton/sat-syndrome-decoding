from utils import *

def build_WXNF(n, anf_filename, xnf_filename):
    """"
    Converts an ANF (Algebraic Normal Form) file into an WXNF1 encoding.

    Args:
        n (int): Total number of variables.
        anf_filename (str): Path to the input file in ANF format.
        xnf_filename (str): Path to the output file in XNF format.
    """
    
    # Read the ANF file and store all lines
    with open(anf_filename, 'r') as anf_file:
        lines = anf_file.readlines()

    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    top_id = n + 1 # n+1 for 'T' (true constant)

    nb_vars = top_id  # Total number of variables including 'T'

    soft_weight = 1
    hard_weight = n * soft_weight + 1

    cnf_clauses = []

    # Soft clauses
    for j in range(1, n+1):
        var_id = e_vars[j-1]
        cnf_clauses.append(f"{soft_weight} -{var_id} 0")

    # Hard clause: the codeword must be non-zero
    hard_clause = " ".join(str(e_vars[j]) for j in range(n))
    cnf_clauses.append(f"{hard_weight} {hard_clause} 0")

    # Skip ANF header, remove the initial 'x' and replace 'T' with top_id
    anf_content = []

    for line in lines[1:]:
        # Remove the 'x', the spaces, and replace 'T' with top_id
        clean_line = line.lstrip().lstrip('x').lstrip().replace('T', str(top_id))
        
        # Extract the variables as a list of integers
        vars_in_line = [int(v) for v in clean_line.split() if v != '0']

        # Separate T from the other variables
        vars_effectives = [v for v in vars_in_line if v != top_id]

        if len(vars_effectives) == 1:
            a = vars_effectives[0]
            # Generate the CNF clause for a single variable
            cnf_clauses.append(f"{hard_weight} -{a} 0")
        elif len(vars_effectives) == 2:
            a, b = vars_effectives
            # Generate CNF clauses for 2-variable XOR
            cnf_clauses.append(f"{hard_weight} {a} -{b} 0")
            cnf_clauses.append(f"{hard_weight} -{a} {b} 0")
        else:
            # Keep the XOR clause for GaussMaxHS
            anf_content.append(f"x {hard_weight} {clean_line}")


    # Total number of clauses = ANF lines (without header) + CNF clauses
    nb_lines = len(anf_content) + len(cnf_clauses)

    # Write the final XNF file
    with open(xnf_filename, 'w') as xnf_file:
        # Write XNF header: p cnf <num_vars> <num_clauses>  10
        xnf_file.write(f"p wcnf {nb_vars} {nb_lines + 1} {hard_weight}\n")

        for clause in cnf_clauses:
            xnf_file.write(clause + "\n")

        # Explicitly write the clause for top_id
        xnf_file.write(f"{hard_weight} {top_id} 0\n")

        # Write ANF lines without header
        xnf_file.writelines(anf_content)
        
    print(f"Conversion complete: {xnf_filename} generated with {nb_vars} variables and {nb_lines} clauses.")