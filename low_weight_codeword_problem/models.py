import os
import argparse
import sys
from utils import parse_input_file, write_wcnf_to_file, process_matrix_and_write_to_file

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Low-Weight Codeword (LWC) instances in WCNF, WXNF or OPB format."
    )
    parser.add_argument("input_file", help="Path to the input challenge file")
    parser.add_argument("-f", "--format", choices=["WCNF1", "WCNF2", "WXNF", "PB1", "PB2"], required=True,
                        help="Output format: WCNF (MaxSAT) WXNF (XOR-extended), or PB1/PB2 (OPB)")
    parser.add_argument("--cc", type=int, default=3, 
                        help="Cardinality encoding (for PySAT CardEnc). Default: 3")
    parser.add_argument("--pb", type=int, default=5, 
                        help="Pseudo-Boolean encoding (for PySAT PBEnc). Default: 5")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    if not os.path.exists(args.input_file):
        log(f"Input file not found: {args.input_file}", "ERROR")
        sys.exit(1)

    # Parse the base challenge parameters
    log(f"Parsing input file: {args.input_file}")
    n, seed, H_transpose = parse_input_file(args.input_file)

    # Generation based on selected format
    if args.format in ("PB1", "PB2"):
        from LW_PB import build_PB1, build_PB2, write_opb_to_file
        variant = int(args.format[-1])
        builder = build_PB1 if variant == 1 else build_PB2
        nb_vars, constraints, objective = builder(n, H_transpose)
        output = write_opb_to_file(args.input_file, seed, variant, nb_vars, constraints, objective)
        log(f"PB{variant} model generated at: {output}")

    elif args.format == "WCNF1":
        from LW_WCNF import build_WCNF1
        log("Building WCNF Variant 1...")
        cnf = build_WCNF1(n, H_transpose, cc_encoding=args.cc, pb_encoding=args.pb)
        write_wcnf_to_file(args.input_file, args.pb, cnf, seed, variant="1")

    elif args.format == "WCNF2":
        from LW_WCNF import build_WCNF2
        log("Building WCNF Variant 2...")
        cnf = build_WCNF2(n, H_transpose, pb_encoding=args.pb)
        write_wcnf_to_file(args.input_file, args.pb, cnf, seed, variant="2")

    elif args.format == "WXNF":
        from LW_WXNF import build_WXNF
        log(f"Generating WXNF for seed {seed}...")
        
        # Prepare filenames and directories
        input_basename = os.path.basename(args.input_file)
        file_no_ext = os.path.splitext(input_basename)[0]
        
        # Path for the intermediate ANF file
        anf_filename = f"Challenges/seed_{seed}/ANF/{file_no_ext}.anf"
        # Path for the final WXNF file
        wcnf_filename = f"Challenges/seed_{seed}/WXNF/{file_no_ext}.wcnf"
        
        # Create necessary directories
        os.makedirs(os.path.dirname(anf_filename), exist_ok=True)
        os.makedirs(os.path.dirname(wcnf_filename), exist_ok=True)
        
        # Process matrix to ANF
        log(f"Writing ANF to: {anf_filename}")
        process_matrix_and_write_to_file(n, H_transpose, anf_filename)
        
        #  Build WXNF from the ANF file
        log(f"Building WXNF at: {wcnf_filename}")
        build_WXNF(n, anf_filename, wcnf_filename)
        
        log("WXNF generation complete.")

    log("Generation process completed successfully.")

if __name__ == "__main__":
    main()
