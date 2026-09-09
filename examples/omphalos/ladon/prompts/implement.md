# Ladon implement session — hint $hint_n (class $hint_class), night $date

## The hint

$hint_context

## The plan entry (what the planning session expects you to build)

$plan_entry

## Your task

1. Read the hint's source entry in `PROGRESS.md` (search `rg --no-ignore
   -n "<key phrase>" PROGRESS.md`) and the code it names. Decide the
   smallest single change that tests the hint.
2. Implement that change under `examples/omphalos/` — product code
   and/or the arm script. One change only.
3. Create the arm script at `$script` from the template below (keep
   the seeds/smoke/output logic exactly; fill the pre-registration
   docstring: idea, the one change, expected effect, expected spend).
4. Check: `ruff format $script` and every file you touched, `ruff
   check` on them, `make test-unit` (in `examples/omphalos`), `make
   pyright` (repository root). If you touched `runtime/pytanque_utils.py`,
   `runtime/rocq_server.py` or `prove_agentic.py`: also `make test-rocq` and
   `make bridge-parity`.
5. Smoke: `LADON_SMOKE=1 LADON_SEEDS=0 python $script run
   --max_workers=2 --wait` — three trainX cells (about a cent). Then
   `LADON_SMOKE=1 LADON_SEEDS=0 python $script status`: it must report
   3 done, 0 failed. Never run the script without both variables: a
   bare `run`, `status` or `--dry` registers every cell of the full arm. Read a
   `result.yaml` only with `head -60` and only if a cell failed.
6. Write `$notes` (markdown): what you changed and why, the files
   touched, the smoke numbers, anything that surprised you, and a
   `## New hints` section — every improvement idea you met on the way,
   one bullet each as `- [tag] Title — body` — or `- none`.
7. Write `$arm_yaml` in exactly this shape:

```yaml
hint: $hint_n
class: $hint_class
title: "<short title of the change>"
summary: "<one sentence: what the arm changes relative to the baseline>"
script: $script
output_dir: $output_dir
smoke_dir: $smoke_dir
expected_effect: solves        # solves | cost | both
touched: [<paths relative to examples/omphalos, including the script>]
smoke: {done: <n>, failed: <n>, solved: <n>, spend_usd: <sum>}
preregistration: "<the decision rule sentence from the docstring>"
ready: true                    # false if no working arm exists; say why in notes
```

## Arm script template (`$script`)

```python
$template
```

## Reminders

- Ladon runs the real experiment itself (`LADON_SEEDS=0`, then
  `LADON_SEEDS=0,1`, on `$output_dir`). Do NOT launch it.
- Do NOT commit. Do NOT edit frozen files (system rules). Do NOT touch
  any other output directory.
- You have at most $max_turns turns; keep the last ten for `notes.md`
  and `arm.yaml`. If the hint needs structural or upstream work, stop
  early, set `ready: false`, and write what a human should do.
