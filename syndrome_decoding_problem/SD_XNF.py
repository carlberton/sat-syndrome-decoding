from pysat.card import *
from utils import *

def build_XNF1(n, w, anf_filename, xnf_filename, encoding):
    """"
    Converts an ANF (Algebraic Normal Form) file into an XNF1 encoding.

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        anf_filename (str): Path to the input file in ANF format.
        xnf_filename (str): Path to the output file in XNF format.
        encoding (str): Cardinality constraint encoding to use.
    """
    
    # Read the ANF file and store all lines
    with open(anf_filename, 'r') as anf_file:
        lines = anf_file.readlines()

    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    top_id = n + 1 # n+1 for 'T' (true constant)

    # Skip ANF header and replace 'T' by top_id in all equations
    anf_content = [line.replace('T', str(top_id)) for line in lines[1:]]

    # Encode the constraint on the total Hamming weight of e
    cnf = CardEnc.atmost(lits=e_vars, top_id=top_id, bound=w, encoding=encoding)
    nb_vars = cnf.nv  # Update top_id

    # Convert the generated CNF clauses to text lines
    cnf_clauses = [" ".join(map(str, clause)) + " 0" for clause in cnf.clauses]

    # Total number of clauses = ANF lines (without header) + AtMost clauses
    nb_lines = len(anf_content) + len(cnf_clauses)

    # Write the final XNF file
    with open(xnf_filename, 'w') as xnf_file:
        # Write XNF header: p cnf <num_vars> <num_clauses>
        xnf_file.write(f"p cnf {nb_vars} {nb_lines + 1}\n")

        # Explicitly write the clause for top_id
        xnf_file.write(f"{top_id} 0\n")
        
        # Append all CNF clauses
        xnf_file.write("\n".join(cnf_clauses) + "\n")

        # Write ANF lines without header
        xnf_file.writelines(anf_content)
        

    print(f"Conversion complete: {xnf_filename} generated with {nb_vars} variables and {nb_lines} clauses.")



def build_XNF2(n, w, anf_filename, xnf_filename, encoding):
    """"
    Converts an ANF (Algebraic Normal Form) file into an XNF2 encoding.

    Args:
        n (int): Total number of variables.
        w (int): Maximum Hamming weight.
        anf_filename (str): Path to the input file in ANF format.
        xnf_filename (str): Path to the output file in XNF format.
        encoding (str): Cardinality constraint encoding to use.
    """

    # Read the ANF file and store all lines
    with open(anf_filename, 'r') as anf_file:
        lines = anf_file.readlines()

    # Variables e_j numbered from 1 to n
    e_vars = list(range(1, n+1))
    top_id = n + 1 # n+1 for 'T' (true constant)
    cnf_lines = []  # Stocker les clauses CNF générées

    # Process each line of the ANF file, skipping the header
    for line in lines[1:]: 
        line = line.strip()
        if not line or not line.startswith('x'):
            continue # Skip empty or malformed lines

        # Extract all variable IDs involved in the current equation, ignoring top_id and trailing zero
        variables = [int(v) for v in line.split() if v.isdigit() and v != str(top_id) and int(v) != 0]

        # If the number of variables exceeds w, encode a local AtMost constraint
        if len(variables) > w:
            cnf = CardEnc.atmost(lits=variables, top_id=top_id, bound=w, encoding=encoding)
            cnf_lines.extend([" ".join(map(str, clause)) + " 0" for clause in cnf.clauses])
            top_id = cnf.nv 

    # Encode the constraint on the total Hamming weight of e
    cnf = CardEnc.atmost(lits=e_vars, top_id=top_id, bound=w, encoding=encoding)
    nb_vars = cnf.nv # Update top_id

    # Convert the generated CNF clauses to text lines
    cnf_lines.extend([" ".join(map(str, clause)) + " 0" for clause in cnf.clauses])

    # Skip ANF header and replace 'T' by top_id in all equations
    anf_content = [line.replace('T', str(top_id)) for line in lines[1:]]
   
    # Total number of clauses = ANF lines (without header) + AtMost clauses
    nb_lines = len(anf_content) + len(cnf_lines)

    # Write the final XNF file
    with open(xnf_filename, 'w') as xnf_file:
        # Write XNF header: p cnf <num_vars> <num_clauses>
        xnf_file.write(f"p cnf {nb_vars} {nb_lines + 1}\n")

        # Explicitly write the clause for top_id
        xnf_file.write(f"{top_id} 0\n")

        # Append all CNF clauses
        xnf_file.write("\n".join(cnf_lines) + "\n")
        
        # Write ANF lines without header
        xnf_file.writelines(anf_content)

    print(f"Conversion complete: {xnf_filename} generated with {nb_vars} variables and {nb_lines} clauses.")