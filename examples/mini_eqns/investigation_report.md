# Mini Equations 100% Success Rate Investigation Report

## Executive Summary

The baseline experiment in `examples/mini_eqns/` shows a suspiciously high 100% success rate across all 60 configurations. After thorough investigation, **this is not a bug but rather reveals important insights about experiment design and benchmark selection**.

## Key Findings

### ✅ System Components Work Correctly

1. **Proof Checker Validation**: The checker (`checker.py`) properly rejects invalid proofs:
   - Correctly identifies malformed YAML
   - Rejects incorrect rule applications
   - Validates proof structure and transitivity
   - Ensures proofs end with target equations

2. **Interactive Feedback System**: The system uses feedback loops effectively:
   - 76.7% of experiments succeed on first attempt
   - 23.3% require feedback corrections (1-3 cycles)
   - Most feedback addresses parse errors (87) vs checker errors (7)
   - Average 1.3 requests per experiment

### 🎯 The Real Issue: Benchmark Selection

The 100% success rate is explained by **strategic benchmark curation**:

**Used Equations (Complexity 22-34)**:
- 3 basic angle identities (cos(π/3) = sin(π/6))
- 6 simple angle shifts (sin(π/2 + x) = cos(x))
- 1 Pythagorean identity (cos²x + sin²x = 1)

**Unused Complex Equations (Complexity 40-82)**:
- Double angle formulas: sin(2x) = 2sin(x)cos(x)
- Half angle formulas: cos(x) = cos²(x/2) - sin²(x/2)
- Sum/difference products: sin(x+y) - sin(x-y) = 2cos(x)sin(y)
- Higher order: sin³(x) = (3sin(x) - sin(3x))/4

**Testing Results**:
- ✅ **Original benchmark**: 100% success (10/10 equations)
- ❌ **Complex equations**: 0% success (0/11 equations)

## Root Cause Analysis

### Why 100% Success Rate on Current Benchmark

1. **Limited Rule Set**: Only 8 basic trigonometric rules available
   - cos_zero, sin_zero, sin_halfpi, cos_halfpi
   - sin_neg, cos_neg, cos_add, sin_add

2. **Curated Equation Selection**: The benchmark only includes equations that:
   - Can be proven using these 8 rules
   - Require relatively short proof chains
   - Are well-represented in LLM training data

3. **Effective Interactive System**: The feedback mechanism helps LLMs:
   - Correct syntax errors in YAML formatting
   - Fix minor rule application mistakes
   - Learn from proof checker feedback

### Why 0% Success on Complex Equations

Complex equations fail because they require:
- Additional trigonometric rules not in the current set
- Longer multi-step proof chains
- More sophisticated mathematical reasoning
- Rules like double angle, triple angle, or product-to-sum formulas

## Implications and Recommendations

### For Research Interpretation

**✅ Positive Findings**:
- The Delphyne framework's interactive proof system works effectively
- LLMs can successfully generate formal proofs with feedback
- The separation of strategies and policies is well-implemented

**⚠️ Limitations to Consider**:
- Current success rate only applies to a carefully selected subset of problems
- Real-world mathematical proof tasks would likely show much lower success rates
- The benchmark doesn't test the system's limits or failure modes

### For Future Experiments

1. **Expand Rule Set**: Add more trigonometric identities to enable complex proofs
2. **Gradual Difficulty Increase**: Include equations of varying complexity levels
3. **Mixed Benchmarks**: Combine solvable and unsolvable equations
4. **Failure Analysis**: Study what types of errors occur with harder problems

## Technical Details

### Experiment Configuration
- **Equations tested**: 10 from `some_htps.txt` (first 10 of 22 available)
- **Models**: gpt-4o-mini, gpt-4o
- **Seeds**: 3 per configuration
- **Budget**: $0.20 per run
- **Feedback cycles**: Up to 3

### Success Patterns by Equation
- **Perfect (100% first attempt)**: sin(π - x) = sin(x), cos(π/3) = sin(π/6)
- **High (83% first attempt)**: cos(π + x) = -cos(x), cos(π/4) = sin(π/4)
- **Medium (50-67% first attempt)**: sin(π/2 + x) = cos(x), cos(2π + x) = cos(x)

## Conclusion

The 100% success rate is **legitimate but narrow in scope**. The experiment successfully demonstrates that:

1. The Delphyne framework can handle well-defined mathematical proof tasks
2. Interactive feedback significantly improves LLM performance on formal reasoning
3. Current LLMs can generate valid trigonometric proofs within known rule sets

However, the results should be interpreted with the understanding that they represent performance on a carefully curated subset of problems that are known to be solvable with the available tools.

The investigation reveals the importance of benchmark design in AI research - successful results on limited benchmarks don't necessarily generalize to broader problem spaces.