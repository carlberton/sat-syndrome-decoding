#!/usr/bin/env python3

import sys
import random
import os
import math

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def usage():
    eprint("ERROR: the script expects 2 integer arguments: 'n' and 'seed'.")
    eprint(" - 'n' is the size of the matrix (H will be of size n//2 * n).")
    eprint(" - 'seed' is the random seed value.")
    eprint("This script generates an instance of the syndrome decoding problem.")
    eprint("The instance will be saved in 'Challenges/seed_${seed}/SD/SD_n_seed'.")

def dGV(n, k):
    d = 0
    aux = 2**(n-k)
    b = 1
    while aux >= 0:
        aux -= b
        d += 1
        b *= (n - d + 1)
        b /= d
    return d 

def main(n, seed):
    w = math.ceil(1.05 * dGV(n, n // 2))
    random.seed(seed)
    text = ""
    text += "# n\n" + str(n) + "\n"
    text += "# seed\n" + str(seed) + "\n"
    text += "# w\n" + str(w) + "\n"
    text += "# H^transpose (each line corresponds to column of H, the identity part is omitted)\n"

    for _ in range(n - n // 2):
        line = "".join(str(random.randint(0, 1)) for _ in range(n // 2))
        text += line + "\n"

    text += "# s^transpose\n"
    s_line = "".join(str(random.randint(0, 1)) for _ in range(n // 2))
    text += s_line + "\n"

    # New directory path
    directory = f"Challenges/seed_{seed}/SD/"
    os.makedirs(directory, exist_ok=True)

    filename = f"{directory}SD_{n}_{seed}"
    with open(filename, "w") as file:
        file.write(text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        exit(1)
    try:
        n = int(sys.argv[1])
        seed = int(sys.argv[2])
    except:
        usage()
        exit(1)
    main(n, seed)
