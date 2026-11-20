import os
import argparse
import sys
from utils import parse_input_file, write_cnf_to_file, process_matrix_and_write_to_file

def log(msg, level="INFO"):
    """Standardized logging function."""
    print(f"[{level}] {msg}")

def parse_args():
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Syndrome Decoding (SD) instances in CNF, XNF or OPB format."
    )
    # Required arguments
    parser.add_argument("input_file", help="Path to the input instance file")
    parser.add_argument("-f", "--format", choices=["CNF1", "CNF2", "XNF1", "XNF2", "PB1", "PB2"], required=True,
                        help="Output format and variant (e.g., CNF1, XNF2, PB1)")
    
    # Parameter options
    parser.add_argument("--cc", type=int, default=3, 
                        help="Cardinality encoding (for PySAT or XNF). Default: 3")
    parser.add_argument("--pb", type=int, 
                        help="Pseudo-Boolean encoding (required for CNF models).")
    parser.add_argument("--w_override", type=int, 
                        help="Override the target weight w from the input file.")
    
    return parser.parse_args()

def main():
    args = parse_args()

    # Check if input file exists before processing
    if not os.path.exists(args.input_file):
        log(f"Input file not found: {args.input_file}", "ERROR")
        sys.exit(1)

    # Parsing input data (n, seed, w, H_transpose, s_transpose)
    log(f"Parsing input file: {args.input_file}")
    n, seed, w, H_transpose, s_transpose = parse_input_file(args.input_file)

    # Apply weight override if provided via CLI
    if args.w_override is not None:
        log(f"Overriding weight: w={w} -> w={args.w_override}")
        w = args.w_override

    # Native pseudo-Boolean formats (no CNF translation).
    if args.format in ("PB1", "PB2"):
        from SD_PB import build_PB1, build_PB2, write_opb_to_file
        variant = int(args.format[-1])
        builder = build_PB1 if variant == 1 else build_PB2
        nb_vars, constraints = builder(n, w, H_transpose, s_transpose)
        output = write_opb_to_file(args.input_file, seed, variant, nb_vars, constraints)
        log(f"PB{variant} model generated at: {output}")

    # Handle CNF Formats
    elif args.format.startswith("CNF"):
        from SD_CNF import build_CNF1, build_CNF2
        if args.pb is None:
            log("Pseudo-Boolean encoding (--pb) is required for CNF models.", "ERROR")
            sys.exit(1)
        
        variant = args.format[-1]  # Extract '1' or '2' from the format string
        log(f"Building CNF Variant {variant}...")
        
        if variant == "1":
            cnf = build_CNF1(n, w, H_transpose, s_transpose, args.cc, args.pb)
        else:
            cnf = build_CNF2(n, w, H_transpose, s_transpose, args.cc, args.pb)

        # Output folder and filename handled by write_cnf_to_file utility
        write_cnf_to_file(args.input_file, args.cc, args.pb, cnf, seed, variant)
        log(f"CNF{variant} model generated successfully.")

    # Handle XNF Formats
    elif args.format.startswith("XNF"):
        from SD_XNF import build_XNF1, build_XNF2
        variant = args.format[-1]
        log(f"Building XNF Variant {variant} for seed {seed}...")

        # Setup directory structure
        anf_dir = f"Challenges/seed_{seed}/ANF"
        xnf_dir = f"Challenges/seed_{seed}/XNF{variant}/encoding_{args.cc}"
        os.makedirs(anf_dir, exist_ok=True)
        os.makedirs(xnf_dir, exist_ok=True)

        input_basename = os.path.splitext(os.path.basename(args.input_file))[0]
        anf_filename = os.path.join(anf_dir, f"{input_basename}.anf")
        xnf_filename = os.path.join(xnf_dir, f"{input_basename}.cnf")

        # Generate ANF (Algebraic Normal Form) if it doesn't exist
        if not os.path.exists(anf_filename):
            log(f"Creating intermediate ANF file at: {anf_filename}")
            process_matrix_and_write_to_file(n, H_transpose, s_transpose, anf_filename)
        else:
            log(f"ANF already exists: {anf_filename}, skipping generation.")

        # Build XNF 
        if variant == "1":
            build_XNF1(n, w, anf_filename, xnf_filename, args.cc)
        else:
            build_XNF2(n, w, anf_filename, xnf_filename, args.cc)

        log(f"XNF{variant} model generated at: {xnf_filename}")

if __name__ == "__main__":
    main()
