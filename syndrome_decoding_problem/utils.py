import os
import re
import subprocess

def parse_input_file(file_name):
    """
    Parse the input file and extract the values n, seed, w, H^T, and s^T.

    Args:
        file_name (str): Path to the input file.

    Returns:
        n (int): Total number of variables.
        seed (int): Random seed used to generate the instance.
        w (int): Maximum Hamming weight.
        H_transpose (list of str): The transposed parity-check matrix.
        s_transpose (str): The syndrome vector.
    """

    with open(file_name, 'r') as f:
        lines = f.readlines()

    n = int(lines[1].strip())  # Extract n
    # print(f"n = {n}")

    seed = int(lines[3].strip())  # Extract the seed
    # print(f"seed = {seed}")

    w = int(lines[5].strip())  # Extract target weight w
    # print(f"w = {w}")

    H_transpose = [line.strip() for line in lines[7:7 + n//2]]  # Read H^transpose matrix
    H_transpose = [''.join(row) for row in zip(*H_transpose)]  # Transpose the matrix
    # print("\nH^transpose:")
    # for row in H_transpose:
    #     print(row)

    s_transpose = lines[7 + n//2 + 1].strip()  # Read s^transpose (syndrome)
    # print("\ns^transpose:")
    # print(s_transpose, "\n")
    
    return n, seed, w, H_transpose, s_transpose


def build_var_sets(H_transpose, s_transpose, n, w):
    """
    Construct the sets V and K.
    
    Args:
        H_transpose (list of str): The transposed parity-check matrix (H^T), one string per row.
        s_transpose (str): The syndrome vector as a string of 0s and 1s.
        n (int): Total number of variables.
        w (int): Parameter controlling the maximum Hamming weight.
    
    Returns:
        V (list of list of int): List of variable index sets for each equation.
        K (list of list of int): Allowed sum values for each equation.
    """
    
    # Build V_{E_i} sets for each equation
    V = []
    for i, row in enumerate(H_transpose):
        V_i = [i + 1]  # Identity variable
        for j, val in enumerate(row):
            if val == '1':
                V_i.append(j + int(n / 2) + 1)
        V.append(V_i)

    # Build K_{E_i} sets (valid cardinalities mod 2)
    K = []
    for i, V_i in enumerate(V):
        max_val = min(len(V_i), w)
        s_i = int(s_transpose[i])
        K_i = [j for j in range(max_val + 1) if j % 2 == s_i]
        K.append(K_i)

    return V, K


def write_cnf_to_file(input_file, cc_encoding, pb_encoding, cnf, seed, variant):
    """
    Save CNF clauses to a file in a structured output directory.

    Args:
        input_file (str): Path to the original input file.
        cc_encoding (str): Cardinality constraint encoding to use.
        pb_encoding (str):  Pseudo-Boolean constraint encoding to use.
        cnf (CNF object): A CNF object.
        seed (int): Random seed used to generate the instance.
    """

    # Generate the output file name based on input and encoding types
    file_name, _ = os.path.splitext(input_file)
    output_file = f"./Challenges/seed_{seed}/CNF{variant}/PB_{pb_encoding}/encoding_{cc_encoding}/{file_name.split('/')[-1]}.cnf"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Create directories if they don't exist
    
    # Save CNF clauses to the file
    cnf.to_file(output_file)
    
    print(f"CNF clauses have been saved to {output_file}")


def extract_SD_n(filename):
    """
        Extracts the number 'n' from filenames like "SD_<n>_*" using regex

        Args:
            filename (str): Filename containing a pattern like "SD_<n>_*".

        Returns:
            n (int): the number of variables in the syndrome decoding instance.
    """
    match = re.search(r"SD_(\d+)_*", filename)
    return int(match.group(1)) if match else float('inf') 



def verify_sol(input_file, solution) :
    """
    Verifies the correctness of a candidate solution for a Syndrome Decoding Problem (SDP)
    by calling an external checker script.

    Args:
        input_file (str): Path to the input file describing the SDP instance.
        solution (str): A binary string representing the candidate solution.

    Returns:
        bool: True if the solution is correct according to the checker, False otherwise.
    """

    if solution:
        try:
            # Call the external Python script to check the solution
            result = subprocess.run(
                ['python3', 'check_SDP_solution.py', input_file, solution],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True
            )
            output = result.stdout.strip()

            # Check if the checker script confirms correctness
            if "The candidate solution is correct." in output:
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            # If the subprocess fails (e.g., script crashes), print the error
            print("Error during external verification:", e.stderr)
    else:
        print("No solution found.")



def process_matrix_and_write_to_file(n, H_transpose, s_transpose, anf_filename):
    """
    Processes the transposed parity-check matrix and syndrome vector,
    then writes the result in ANF (Algebraic Normal Form) format to a file.

    Args:
        n (int): Total number of variables.
        H_transpose (list of str): Transposed parity-check matrix.
        s_transpose (str): Syndrome vector.
        anf_filename (str): Path to the output file in ANF format.
    """

    m = len(s_transpose)
    lines_to_write = []

    # Add ANF header: format is "p anf <number of variables> <number of equations>"
    header = f"p anf {n} {m}"
    lines_to_write.append(header)

    # Construct each equation line in ANF format
    for i in range(m):
        line = [str(i + 1)] # Start with the variable index of the identity part
        # For each 1 in H_transpose[i][j], add the corresponding variable index
        for j in range(m):
            if H_transpose[i][j] == '1':
                line.append(str(j + m + 1))
        
        # If the syndrome bit is 0, add the constant term 'T' (i.e., True constant)
        if s_transpose[i] == '0':
            line.append('T')
        
        # End the equation line with '0' to signal termination
        line.append('0')
        # Add the formatted line with 'x' prefix
        lines_to_write.append(f"x {' '.join(line)}")  

    # Write all lines to the output ANF file
    with open(anf_filename, 'w') as file:
        for line in lines_to_write:
            file.write(line + '\n')

    print(f"Results successfully written to {anf_filename}")