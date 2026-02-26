import os
import sys
import csv

csv.field_size_limit(sys.maxsize)

def parse_input_file(file_name):
    """Parses the input file and extracts the necessary information."""
    with open(file_name, 'r') as f:
        lines = f.readlines()

    n = int(lines[1].strip())  # Get n
    print(f"n = {n}")

    w = int(lines[5].strip())  # Retrieve the target weight w
    print(f"w = {w}")

    r = n // 2  # Number of lines of the syndrome (and size of identity)
    P_cols = [line.strip() for line in lines[7:7 + r]]  # Columns of P (= rows of H^T)

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
    
    #In the display, one row corresponds to one column, which is more practical for calculations.
    H_transpose = [''.join(row) for row in zip(*H_transpose)]

    print("\nH^T ")
    for col in H_transpose:
        print(col)

    s_transpose = lines[7 + r + 1].strip()  # Syndrome s^T
    print("\ns^T :")
    print(s_transpose, "\n")

    return n, w, H_transpose, s_transpose



    
def verify_solution(candidate, H_transpose, s, w, n):
    # Candidate length verification
    if len(candidate) != n:
        raise ValueError(f"The candidate vector must be of length {n}, but it is of length {len(candidate)}.")

    # Weight check (number of bits set to 1)
    weight = candidate.count('1')
    print(f"--- Weight of the solution: {weight} ---")
    if weight > w:
        print(f"Failure: the candidate solution contains {weight} bits set to 1 (maximum allowed: {w}).")
        return False, None

    syndrome = ""
    # For each column, we calculate the dot product
    for colonne in H_transpose:
        # We check the length of the candidate solution and the column
        if len(colonne) != len(candidate):
            raise ValueError("The size of a column and the vector do not match.")

        # Calculating the dot product modulo 2
        somme = sum(int(bit_col) * int(bit_vect) for bit_col, bit_vect in zip(colonne, candidate))
        syndrome += str(somme % 2)

    if syndrome == s:
        return True, syndrome
    else:
        return False, syndrome


def extract_binary_solution(csv_path, target_file_name, n):
    """
    Reads the CSV and extracts the binary solution for a specific challenge.
    Supports two formats in the 'Solution' column:
    1. Raw binary strings: "010110..."
    2. SAT literals: "-1 2 -3 4 0"
    """
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, mode='r', encoding='utf-8') as f:
        # Using DictReader - Ensure your CSV header uses 'File' and 'Solution'
        reader = csv.DictReader(f, delimiter=',')
        
        for row in reader:
            # Match the challenge filename
            if row['File'] == os.path.basename(target_file_name):
                print(f"Found matching entry for {target_file_name} in CSV.")
                solution_str = row['Solution'].strip()
                
                # Case 1: The solution is already a binary string
                if all(c in "01" for c in solution_str) and len(solution_str) >= n:
                    # We take only the first n bits in case there is trailing padding
                    return solution_str[:n]
                
                # Case 2: The solution is in SAT literal format (-1 2 -3...)
                values = solution_str.split()
                bits = []
                for v in values:
                    if v == '0' or len(bits) == n:
                        break
                    try:
                        val = int(v)
                        bit = '1' if val > 0 else '0'
                        bits.append(bit)
                    except ValueError:
                        # Skip non-integer values if they exist
                        continue
                
                return ''.join(bits)

    return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python check_SDP_solution.py <input_file> <csv_file_or_solution>")
        sys.exit(1)

    input_file = sys.argv[1]  # SD File
    candidate_arg = sys.argv[2]  # Either a CSV file or a binary string
    
    # Parse the input file
    n, w, H, s = parse_input_file(input_file)

    # Checking if the second argument is a file (CSV) or a direct solution
    if os.path.isfile(candidate_arg):  
        # If it's a file, we interpret it as a CSV.
        candidate = extract_binary_solution(candidate_arg, input_file, n)
        if candidate is None:
            print(f"No solution found for {input_file} in {candidate_arg}.")
            sys.exit(1)
    else:
        # Otherwise, we take the argument directly as a candidate solution.
        candidate = candidate_arg

        # Verify that the string is indeed a sequence of 0s and 1s of length n
        if not all(c in "01" for c in candidate) or len(candidate) != n:
            print("Error: The provided candidate solution is not valid.")
            sys.exit(1)

    print(f"Candidate solution: {candidate}")

    # Verification
    valid, computed_syndrome = verify_solution(candidate, H, s, w, n)

    if valid:
        print(f"The candidate solution is correct. Computed syndrome: {computed_syndrome}")
    else:
        print(f"The candidate solution is NOT correct. Computed syndrome: {computed_syndrome}")

if __name__ == "__main__":
    main()
