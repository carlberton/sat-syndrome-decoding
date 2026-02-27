# SAT-Based Syndrome Decoding and Low-Weight Codeword Problem

This repository contains source code and instance generators for modelling Syndrome Decoding and Low-weight Codeword problems using Satisfiability (SAT) and Maximum Satisfiability (MaxSAT) both in XNF and CNF formats.

---

## Environment Setup

It is recommended to use a Python virtual environment (Python 3.8+) to manage dependencies.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

## Syndrome Decoding Problem (SDP)

Generate original SDP instance

```bash
# Generate instances for a specific size 'n' and seed 's'
python3 syndrome_generate.py ${n} ${s} 
```

Generate CNF/XNF models

```bash 
python3 models.py <instance_file> -f <model> --cc <cardinality_encoding> --pb <pseudo_boolean_encoding>
```

Verify if a solution (binary string or CSV output) is correct for a given challenge

```bash
# from a result file:
python3 check_SDP_solution.py <instance_file> <result_csv>
```

```bash
# from a binary string:
python3 check_SDP_solution.py <instance_file> <binary_string>
```

## Low-Weight Codeword Problem (LWCP)

Generate original LWCP instance

```bash
# Generate instances for a specific size 'n' and seed 's'
python3 lowweight_generate.py ${n} ${s}
```

Generate CNF/XNF models

```bash
python3 models.py <instance_file> -f <model> --cc <cardinality_encoding> --pb <pseudo_boolean_encoding>
```

Verify solutions

```bash
# from a result file:
python3 check_LWCP_solution.py <instance_file> <result_csv>
```

```bash
# from a binary string:
python3 check_LWCP_solution.py <instance_file> <binary_string>
```

---

## References 

* **Carl Berton, Sami Cherif, and Claire Delaplace.** *SAT-Based Syndrome Decoding and Low-Weight Codewords.* In 27th International Symposium on Formal Methods (FM 2026), Tokyo, Japan. To appear.
* **Carl Berton, Sami Cherif, and Claire Delaplace.** *Satisfiabilité pour le décodage par syndrome.* In Journées Francophones de Programmation par Contraintes (JFPC 2025), Dijon, France. [⟨hal-05208088⟩](https://hal.science/hal-05208088)






