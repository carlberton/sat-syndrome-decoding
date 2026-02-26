import os
import re
import subprocess

def parse_input_file(file_name):
    """Parse the input file"""
    with open(file_name, 'r') as f:
        lines = f.readlines()

    n = int(lines[1].strip())  # Get n
    print(f"n = {n}\n")

    seed = int(lines[3].strip())  # Retrieve the seed
    print(f"seed = {seed}\n")

    H_transpose = [line.strip() for line in lines[5:5 + n//2]]  # H^T matrix
    H_transpose = [''.join(row) for row in zip(*H_transpose)]
    print("H^T :")
    for row in H_transpose:
        print(row)
    
    return n, seed, H_transpose

def write_wcnf_to_file(input_file, encoding, cnf, seed, variant):
    """Écrit les clauses CNF dans un fichier au format spécifié."""

    # Extract the filename without the extension
    file_name = os.path.splitext(os.path.basename(input_file))[0]

    # Build the exit path
    output_file = f"./Challenges/seed_{seed}/WCNF{variant}/encoding_{encoding}/{file_name}.wcnf"
    
    # Create the folders if needed
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the CNF to the file
    cnf.to_file(output_file)
    
    print(f"The CNF clauses have been registered in {output_file}")


def extract_n(filename):
    match = re.search(r"LW_(\d+)_*", filename)
    return int(match.group(1)) if match else float('inf') 


def verify_sol(input_file, solution) :
    if solution:
        try:
            result = subprocess.run(
                ['python3', 'check_LWCP_solution.py', input_file, solution],
                capture_output=True, text=True, check=True
            )
            output = result.stdout.strip()
            if "The candidate solution is correct." in output:
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            print("Error during external verification:", e.stderr)
    else:
        print("No solution found.")


def process_matrix_and_write_to_file(n, H_transpose, anf_filename):
    """
    Processes the transposed parity-check matrix and syndrome vector,
    then writes the result in ANF (Algebraic Normal Form) format to a file.

    Args:
        n (int): Total number of variables.
        H_transpose (list of str): Transposed parity-check matrix.
        s_transpose (str): Syndrome vector.
        anf_filename (str): Path to the output file in ANF format.
    """

    m = n//2  # Number of equations
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
        
        # Append 'T' to represent the constant term
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
    