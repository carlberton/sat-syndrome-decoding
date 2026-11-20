"""Native pseudo-Boolean optimization models for binary LWCP."""

import os


def _constraint(terms, relation, rhs):
    """Format a linear pseudo-Boolean constraint using signed coefficients."""
    return " ".join(f"{coef:+d} x{var}" for coef, var in terms) + f" {relation} {rhs} ;"


def _build_pb(n, V, K, variant):
    """Return the number of variables and the native PB constraints."""
    if variant not in (1, 2):
        raise ValueError("variant must be 1 or 2")
    if any(not values for values in K):
        # Explicit contradiction, with no new variables.
        return n, [_constraint([(1, 1)], ">=", 2)]

    top_id = n
    constraints = []
    for V_i, K_i in zip(V, K):
        # PB2 needs a variable only for values above the first admissible value.
        values = K_i if variant == 1 else K_i[1:]
        x_vars = {}
        for v in values:
            top_id += 1
            x_vars[v] = top_id

        terms = [(1, j) for j in V_i]
        if variant == 1:
            # One-hot selection and weighted sum equality.
            constraints.append(_constraint([(1, x_vars[v]) for v in K_i], "=", 1))
            terms.extend((-v, x_vars[v]) for v in K_i if v != 0)
            constraints.append(_constraint(terms, "=", 0))
        else:
            # Unary selection: K_i is an arithmetic progression of step 2.
            terms.extend((-2, x_vars[v]) for v in values)
            constraints.append(_constraint(terms, "=", K_i[0]))
            for prev, v in zip(values, values[1:]):
                constraints.append(_constraint([(1, x_vars[prev]), (-1, x_vars[v])], ">=", 0))

    return top_id, constraints


def write_opb_to_file(input_file, seed, variant, nb_vars, constraints, objective=None):
    """Write an OPB instance in Challenges/seed_<seed>/PB<variant>/ ."""
    basename = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join("Challenges", f"seed_{seed}", f"PB{variant}")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, basename + ".opb")
    with open(output_file, "w", encoding="ascii") as f:
        f.write(f"* #variable= {nb_vars} #constraint= {len(constraints)}\n")
        if objective is not None:
            f.write("min: " + " ".join(f"{coef:+d} x{var}" for coef, var in objective) + " ;\n")
        for constraint in constraints:
            f.write(constraint + "\n")
    return output_file


def _build_lwcp(n, H_transpose, variant):
    V = [[i + 1] + [j + n // 2 + 1 for j, val in enumerate(row) if val == "1"]
         for i, row in enumerate(H_transpose)]
    K = [list(range(0, len(V_i) + 1, 2)) for V_i in V]
    nb_vars, constraints = _build_pb(n, V, K, variant)
    # Nonzero codeword and minimization of its Hamming weight.
    objective = [(1, j) for j in range(1, n + 1)]
    constraints.append(_constraint(objective, ">=", 1))
    return nb_vars, constraints, objective


def build_PB1(n, H_transpose):
    return _build_lwcp(n, H_transpose, 1)


def build_PB2(n, H_transpose):
    return _build_lwcp(n, H_transpose, 2)
