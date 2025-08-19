import checker as ch

# You can hardcode or read from a file / input later
N_EXAMPLE_PROOF = """
2:
    - ["cos(0)", "1"] 
    - {rule: cos_zero, vars: {}} 
"""


EXAMPLE_PROOF = """
1:
    - ["cos(pi/4)", "cos(- pi/4)"]
    - {rule: cos_neg, vars: {x: "-pi/4"}}
2:
    - ["cos(pi/2 - pi/4)", "cos(pi/4)"]
    - {rule: sin_add, vars: {x: "pi/4", y: "pi/4"}}
3:
    - ["sin(pi/4)", "cos(pi/4)"]
    - {sym: 1}
"""

def main():
    # You can change this or read from a file using sys.argv[1]
    #target_eq: ch.Eq = ("cos(0)", "1")
    target_eq: ch.Eq = ("sin(pi/4)", "cos(pi/4)")

    proof_or_error = ch.parse_proof(EXAMPLE_PROOF)

    if isinstance(proof_or_error, ch.ParseError):
        print("Parsing failed:")
        print(proof_or_error.msg)
        return

    proof = proof_or_error

    result = ch.check(target_eq, proof, ch.TRIG_RULES)

    if result is None:
        print("✅ Proof is valid!")
    else:
        print("❌ Proof is invalid!")
        print(result)

if __name__ == "__main__":
    main()
