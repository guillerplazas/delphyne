# Proving Math Equalities with Delphyne

This folder contains an example of using Delphyne to generate machine-checkable proofs of simple trigonometric equalities. It is inspired by the _Equations_ environment from the [HyperTree Proof Search paper](https://arxiv.org/pdf/2205.11491).


## Benchmark

We list here all the trigonometric identities from Table 9 of the HyperTree Proof Search paper (linked above).

```
sin(pi/2 + x) = cos(x)
cos(pi/2 - x) = sin(x)
cos(pi + x) = -cos(x)
sin(pi - x) = sin(x)
cos(pi/3) = sin(pi/6)
cos(pi/4) = sin(pi/4)
cos(pi/6) = sin(pi/3)
cos(2*pi + x) = cos(x)
sin(2*pi + x) = sin(x)

cos(x)**2 + sin(x)**2 = 1
cos(x) = cos(x/2)**2 - sin(x/2)**2
sin(x + y) - sin(x - y) = 2*cos(x)*sin(y)
cos(x - y) + cos(x + y) = 2*cos(x)*cos(y)
sin(2*x) = 2*sin(x)*cos(x)
cos(2*x) = 1 - 2*sin(x)**2
cos(2*x) = 2*cos(x)**2 - 1
sin(x) = 2*sin(x/2)*cos(x/2)
cos(x + y)*cos(x - y) = cos(x)**2 - sin(y)**2
sin(x + y)*sin(y - x) = cos(x)**2 - cos(y)**2
sin(x)**3 = (3*sin(x) - sin(3*x))/4
sin(3*x) = 3*sin(x) - 4*sin(x)**3
sin(4*x) = cos(x)*(4*sin(x) - 8*sin(x)**3)
```

Used as examples in prompts:

```
cos(pi/3) = sin(pi/6)
2*sin(x/2)*cos(x/2) = sin(x)
```


## Checker Robustness

The initial experiments had 4 failures caused by LLMs producing malformed mathematical notation that crashed the SymPy parser:

- **Bracket notation**: `[sin(x)]` instead of `sin(x)`
- **Caret exponentiation**: `cos^2(x)` instead of `cos(x)**2`
- **Other syntax errors**: Various non-standard mathematical notations

These parsing errors would crash the experiment entirely instead of providing feedback to the LLM.

**Fix implemented in `checker.py`**: The SymPy parsing is now wrapped to catch parsing exceptions and convert them to `ProofError` with helpful error messages. This allows the feedback loop to continue and potentially recover, rather than crashing the entire experiment.


## Running Experiments

### Prerequisites

- OpenAI API key configured (`OPENAI_API_KEY` environment variable)
- Delphyne installed in dev mode: `pip install -e ".[dev]"`

### Experiment Commands

| Command | Description |
|---------|-------------|
| `python experiments/baseline_experiment.py run` | Run all experiments (parallel by default) |
| `python experiments/baseline_experiment.py run --max_workers=1` | Run experiments sequentially |
| `python experiments/baseline_experiment.py run --retry_errors` | Re-run failed experiments |
| `python experiments/baseline_experiment.py status` | Check experiment progress |
| `python experiments/baseline_experiment.py list` | List all configurations |
| `python experiments/baseline_experiment.py clean_index` | Reset experiment state |
| `python analyze_logs.py` | Analyze results and generate statistics |

### Experiment Grid

| Parameter | Values |
|-----------|--------|
| Equations | All from `benchmark/equations.txt` (26 total) |
| Models | `gpt-4o-mini`, `gpt-4o` |
| Temperature | 1.0 |
| Feedback cycles | 5 (max) |
| Seeds | 0, 1, 2 |
| **Total** | **156 configurations** |

### Expected Cost

| Model | Cost per Run | Notes |
|-------|--------------|-------|
| gpt-4o-mini | ~$0.002 | 78 runs = ~$0.16 |
| gpt-4o | ~$0.025 | 78 runs = ~$1.95 |
| **Total** | | **~$2.11** |


## Performance Results

*Results pending - run `python analyze_logs.py` after experiments complete.*


## Future Work

### Short-term

1. **Expand rule set**: Add double angle (`sin_double`, `cos_double`), half angle, product-to-sum, and Pythagorean identity rules
2. **Improve prompts**: Add more examples covering complex multi-step proofs
3. **Robustify checker**: Better error messages and handling of malformed LLM output

### Medium-term

4. **Benchmark stratification**: Create difficulty tiers (easy/medium/hard) based on proof length
5. **Alternative strategies**: Test single-shot vs interactive, beam search with multiple candidates
6. **Cost optimization**: Prompt length reduction, early termination on likely failures

### Long-term

7. **Advanced search algorithms**: Tree-based proof search with value estimation (similar to HTPS)
8. **Generalization**: Support algebraic identities beyond trigonometry
9. **External integration**: Connect with theorem provers like Lean or Coq