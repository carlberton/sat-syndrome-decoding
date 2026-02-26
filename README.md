# SAT-Based Syndrome Decoding and Low-Weight Codeword Discovery

This repository contains the source code, instance generators, and solvers associated with research on the hardness of decoding linear codes using SAT and CP techniques.

**Reference Publications:**
* **"Satisfiabilité pour le décodage par syndrome"** — *JFPC 2025*, Dijon, France.
* **"SAT-Based Syndrome Decoding and Low-Weight Codewords"** — *To appear in: The 27th International Symposium on Formal Methods (FM 2026)*, Tokyo, Japan.

---

## Installation & Environment Setup

It is recommended to use a Python virtual environment (Python 3.8+) to manage dependencies.

```bash
# 1. Create the virtual environment
python3 -m venv venv

# 2. Activate the environment
source venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

## Syndrom Decoding Problem (SDP)
```bash
cd syndrome_decoding_problem/
```

1. Generate Base Instances
```bash
$ python3 syndrome_decoding_problem/syndrome_generate.py -h
```
```bash
# Example: Generate instances for n from 10 to 150
for n in {10..150..10}; do 
    python3 syndrome_generate.py ${n} 0; 
done
```

2. Generate SAT/XNF Models

Use models.py to transform base instances into CNF or XNF formats.

```bash
$ python3 models.py -h
```
```bash 
# Generate CNF (Variant 2, CC encoding 3, PB encoding 5) 
for n in {10..150..10}; do 
    python3 models.py Challenges/seed_0/SD/SD_${n}_0 -f CNF2 --cc 3 --pb 5; 
done
```
```bash
# Generate XNF (Variant 1, CC encoding 3)
for n in {10..150..10}; do 
    python3 models.py Challenges/seed_0/SD/SD_${n}_0 -f XNF1 --cc 3; 
done
```

3. Solve with CP-SAT

Use the Google OR-Tools CP-SAT solver to generate and solve instances directly.

```bash
python3 SD_CPSAT.py -h
```

```bash
# Solve a single file
python3 SD_CPSAT.py -m CNF2 -f Challenges/seed_0/SD/SD_20_0
```

```bash
# Solve an entire directory
python3 SD_CPSAT.py -m CNF1 -d Challenges/seed_0/SD/
```

4. Verify Solutions

Verify if a solution (binary string or CSV output) is correct for a given challenge.

```bash
python3 check_SDP_solution.py -h
```

```bash
python3 check_SDP_solution.py Challenges/seed_0/SD/SD_20_0 Challenges/seed_0/SD/CPSAT_CNF1_SD_10_0.csv
```

```bash
python3 check_SDP_solution.py Challenges/seed_0/SD/SD_20_0 00000001010000000000
```

## Low-Weight Codeword Problem (LWCP)

```bash
$ cd low_weight_codeword_problem/
```

1. Generate Base Instances

```bash
python3 lowweight_generate.py -h
```

```bash
# Example: Generate instances for n=10 to 150 with seed 0
for n in {10..150..10}; do 
    python3 lowweight_generate.py ${n} 0
done
```

2. Generate WCNF/WXNF Models

Transform base instances into Weighted CNF (for MaxSAT) or Weighted XNF.

```bash
python3 models.py -h
```

```bash
# WCNF Generation
python3 models.py -f WCNF1 --cc 3 --pb 5 Challenges/seed_0/LW/LW_30_0
```

```bash
# WXNF Generation
python3 models.py -f WXNF Challenges/seed_0/LW/LW_30_0
```

3. Generate and solve with CP-SAT

```bash
python3 LW_WCNF_CPSAT.py -h
```
  
```bash
python3 LW_WCNF_CPSAT.py -m CNF1 -f Challenges/seed_0/LW/LW_30_0
```

```bash
 $ python3 LW_WCNF_CPSAT.py -m CNF2 -d Challenges/seed_0/LW/
```
 
4. Verify Solutions

```bash
python3 check_LWCP_solution.py -h
```

```bash
python3 check_LWCP_solution.py Challenges/seed_0/LW/LW_30_0 Challenges/seed_0/LW/CPSAT_WCNF1_LW_30_0.csv
```

```bash
python3 check_LWCP_solution.py Challenges/seed_0/LW/LW_30_0 001010000001000000000010000000
```

## References 
```bibtex
@inproceedings{berton:hal-05208088,
  TITLE = {{Satisfiabilit{\'e} pour le d{\'e}codage par syndrome}},
  AUTHOR = {Berton, Carl and Cherif, Sami and Delaplace, Claire},
  URL = {https://hal.science/hal-05208088},
  BOOKTITLE = {{Journ{\'e}es Francophones de Programmation par Contraintes (JFPC 2025)}},
  ADDRESS = {Dijon, France},
  YEAR = {2025},
  MONTH = Jun,
  KEYWORDS = {Cryptographie ; Satisfiabilit{\'e} ; D{\'e}codage par syndrome},
  PDF = {https://hal.science/hal-05208088v1/file/JFPC25_paper_22.pdf},
  HAL_ID = {hal-05208088},
  HAL_VERSION = {v1},
}
```





