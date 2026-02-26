import os
import sys
import csv

csv.field_size_limit(sys.maxsize)

def parse_input_file(file_name):
    """Parse the input file."""
    with open(file_name, 'r') as f:
        lines = f.readlines()

    n = int(lines[1].strip())  # Get n
    # print(f"n = {n}")

    r = n // 2  # Number of lines of the syndrome (and size of identity)
    P_cols = [line.strip() for line in lines[5:5 + r]]  # Columns of P (= rows of H^T)

    # Construction of H^T with I above
    H_transpose = []
    for i in range(n):
        if i < r:
            # Column i of the identity
            identity_part = ['0'] * r
            identity_part[i] = '1'
            column = ''.join(identity_part)
        else:
            # Column of P at index i - r
            column = P_cols[i - r]
        H_transpose.append(column)
    
    # In the display, one row corresponds to one column, which is more practical for calculations.
    H_transpose = [''.join(row) for row in zip(*H_transpose)]

    # print("\nH^transpose ")
    # for col in H_transpose:
    #     print(col)

    return n, H_transpose


    
def verify_solution(candidate, H_transpose, n):
    # Candidate length verification
    if len(candidate) != n:
        raise ValueError(f"The candidate vector must be of length {n}, but it is of length {len(candidate)}.")

    syndrome = ""
    # For each column, we calculate the dot product
    for colonne in H_transpose:
        # We check the length of the candidate solution and the column
        if len(colonne) != len(candidate):
            raise ValueError("The size of a column and the vector do not match.")

        # Calculating the dot product modulo 2
        somme = sum(int(bit_col) * int(bit_vect) for bit_col, bit_vect in zip(colonne, candidate))
        syndrome += str(somme % 2)

    # print(syndrome)
    if set(syndrome) == {"0"}:
        return True, syndrome
    else:
        return False, syndrome
    

def extraire_solution_binaire(CSV_path, target_file_name, n):
    with open(CSV_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        
        for row in reader:
            if row['File'] == os.path.basename(target_file_name):
                solution_str = row['Solution'].strip()

                # Case 1: if all characters are '0' or '1'
                if all(c in '01' for c in solution_str.replace(" ", "")):
                    # Nettoie et tronque à n bits
                    solution_binaire = ''.join(solution_str.split())[:n]
                    return solution_binaire

                # Case 2: otherwise, we assume a list of signed integers
                valeurs = solution_str.split()
                bits = []
                for v in valeurs:
                    if v == '0' or len(bits) == n:
                        break
                    val = int(v)
                    bit = '1' if val > 0 else '0'
                    bits.append(bit)
                
                return ''.join(bits)
    
    return None



def main():
    if len(sys.argv) < 3:
        print("Usage : python check_LWCP_solution.py <input_file> <CSV_file_or_solution>")
        sys.exit(1)

    input_file = sys.argv[1]  # LWCD File
    candidate_arg = sys.argv[2]  # Either a CSV file or a binary string
    print(f"File : {input_file}")
    
    # Parse the input file
    n, H = parse_input_file(input_file)

    # Checking if the second argument is a file (CSV) or a direct solution
    if os.path.isfile(candidate_arg):  
        # If it's a file, we interpret it as a CSV.
        candidate = extraire_solution_binaire(candidate_arg, input_file, n)
        if candidate is None:
            print(f"No solution found for {input_file} in {candidate_arg}.")
            sys.exit(1)
    else:
        candidate = candidate_arg
        # If it's not a file, we assume it's a direct binary solution. We check its validity.
        if not all(c in "01" for c in candidate) or len(candidate) != n:
            print("The provided solution must be a binary string of length n.")
            sys.exit(1)

    # Verification
    print(f"Candidate solution : {candidate}")
    valid, computed_syndrome = verify_solution(candidate, H, n)
    if valid:
        print(f"The candidate solution is correct. Calculated syndrome: {computed_syndrome}")
    else:
        print(f"The candidate solution is incorrect. Calculated syndrome: {computed_syndrome}")

if __name__ == "__main__":
    main()