from __future__ import annotations

from pathlib import Path
import sys

import nbformat as nbf

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import report_utils as ru

NOTEBOOK_PATH = SCRIPT_DIR / "mini_eqns_report.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(text.strip("\n"))


def first_row(frame, family: str, model: str, effort: str):
    subset = frame.loc[
        (frame["family"] == family)
        & (frame["model_name"].astype(str) == model)
        & (frame["reasoning_effort"].astype(str) == effort)
    ]
    return subset.iloc[0]


paths = ru.find_report_paths(SCRIPT_DIR)
benchmarks = ru.load_benchmarks(paths.benchmark_file)
runs = ru.load_report_runs(paths.report_root)
inventory = ru.build_experiment_inventory(runs)
best_configs = ru.select_best_configs(inventory)

num_baseline = int((inventory["family"] == "baseline").sum())
num_guided = int((inventory["family"] == "guided").sum())
num_step = int((inventory["family"] == "step_by_step").sum())

best_baseline = best_configs.loc[best_configs["family"] == "baseline"].iloc[0]
best_guided = best_configs.loc[best_configs["family"] == "guided"].iloc[0]
best_step = best_configs.loc[best_configs["family"] == "step_by_step"].iloc[0]

base54_low = first_row(inventory, "baseline", "gpt-5.4", "low")
base54_medium = first_row(inventory, "baseline", "gpt-5.4", "medium")
base54_high = first_row(inventory, "baseline", "gpt-5.4", "high")
base54_xhigh = first_row(inventory, "baseline", "gpt-5.4", "xhigh")
base_mini_low = first_row(inventory, "baseline", "gpt-5.4-mini", "low")
base_nano_medium = first_row(inventory, "baseline", "gpt-5.4-nano", "medium")
base_nano_high = first_row(inventory, "baseline", "gpt-5.4-nano", "high")

guided54_low = first_row(inventory, "guided", "gpt-5.4", "low")
guided54_medium = first_row(inventory, "guided", "gpt-5.4", "medium")
guided54_high = first_row(inventory, "guided", "gpt-5.4", "high")
guided_mini_low = first_row(inventory, "guided", "gpt-5.4-mini", "low")
guided_mini_high = first_row(inventory, "guided", "gpt-5.4-mini", "high")

step_replicates = inventory.loc[
    (inventory["family"] == "step_by_step")
    & (inventory["model_name"].astype(str) == "gpt-5.4")
    & (inventory["reasoning_effort"].astype(str) == "low")
].copy().sort_values(["solved", "total_cost"], ascending=[False, True])
step_replicates_min_solved = int(step_replicates["solved"].min())
step_replicates_max_solved = int(step_replicates["solved"].max())
step_replicates_min_cost = float(step_replicates["total_cost"].min())
step_replicates_max_cost = float(step_replicates["total_cost"].max())
step_replicate_labels = ", ".join(ru.experiment_short_label(str(name)) for name in step_replicates["experiment_name"])

step_mini_low = first_row(inventory, "step_by_step", "gpt-5.4-mini", "low")
step_nano_low = first_row(inventory, "step_by_step", "gpt-5.4-nano", "low")

step_advantage = ru.build_step_advantage_table(
    runs,
    benchmarks,
    str(best_baseline["experiment_name"]),
    str(best_guided["experiment_name"]),
    str(best_step["experiment_name"]),
)

BENCHMARK_GROUPS = {
    "001": "phase shifts",
    "002": "phase shifts",
    "003": "phase shifts",
    "004": "phase shifts",
    "005": "special angles",
    "006": "special angles",
    "007": "special angles",
    "008": "periodicity",
    "009": "periodicity",
    "010": "pythagorean",
    "011": "double-angle / half-angle",
    "012": "sum-product transforms",
    "013": "sum-product transforms",
    "014": "double-angle / half-angle",
    "015": "double-angle / half-angle",
    "016": "double-angle / half-angle",
    "017": "double-angle / half-angle",
    "018": "derived product identities",
    "019": "derived product identities",
    "020": "higher-order sine rewrites",
    "021": "higher-order sine rewrites",
    "022": "higher-order sine rewrites",
}

model_failure_runs = runs.copy()
model_failure_runs["analysis_model"] = model_failure_runs["model_name"].astype(str)
step_mask = model_failure_runs["family"] == "step_by_step"
model_failure_runs.loc[step_mask, "analysis_model"] = model_failure_runs.loc[step_mask, "step_model_name"].astype(str)
model_failure_runs["identity_family"] = model_failure_runs["bench_name"].map(BENCHMARK_GROUPS)
model_failure_runs["failed"] = ~model_failure_runs["success"]
model_failure_summary = (
    model_failure_runs.groupby(["analysis_model", "identity_family"], dropna=False)
    .agg(failures=("failed", "sum"), total=("failed", "size"))
    .reset_index()
)
model_failure_summary["failure_rate"] = model_failure_summary["failures"] / model_failure_summary["total"]


def top_family(model: str, rank: int = 0):
    subset = model_failure_summary.loc[model_failure_summary["analysis_model"] == model].sort_values(
        ["failure_rate", "failures", "identity_family"], ascending=[False, False, True]
    )
    return subset.iloc[rank]


gpt54_top = top_family("gpt-5.4", 0)
gpt54_second = top_family("gpt-5.4", 1)
mini_top = top_family("gpt-5.4-mini", 0)
mini_second = top_family("gpt-5.4-mini", 1)
mini_third = top_family("gpt-5.4-mini", 2)
nano_top = top_family("gpt-5.4-nano", 0)
nano_second = top_family("gpt-5.4-nano", 1)
nano_third = top_family("gpt-5.4-nano", 2)

intro_md = f"""
# Mini Equations Experiment Report

This notebook reviews the curated experiments in `examples/mini_eqns/experiments/report`. The report directory now contains **{num_baseline} baseline runs**, **{num_guided} guided runs**, and **{num_step} step-by-step runs** over the 22-equation benchmark.

The notebook stays selective on purpose. Rather than repeating every raw table, it focuses on the comparisons that matter for the report draft: how reasoning effort changes each strategy, whether `mini` or `nano` are worth using, what the newly added `step_by_step` runs change in the overall picture, and where each model still tends to fail.
"""

method_md = """
## Methodology

All configuration metadata is recovered from `experiment.yaml`, while solved counts and cost come from `results_summary.csv`. The summary matrices below show solved equations out of 22, total run cost, and a short experiment label.

Two legacy baseline runs use reasoning effort `None`: `baseline_experiment_1` and `baseline_experiment_6`. That label is carried explicitly in this report rather than being treated as missing metadata. For the current step-by-step runs, the sketch planner is fixed at `gpt-5.4` with `medium` reasoning effort, so the visible variation comes from the step executor.
"""

baseline_md = f"""
## Baseline

The baseline sweep still tells a clean story. A modest amount of forced reasoning helps standard `gpt-5.4`, but pushing reasoning harder stops paying off.

### Supported takeaways

- For standard `gpt-5.4`, `low` and `medium` tie at **19/22**, but `low` is the better choice because it costs **{ru.precise_money(float(base54_low['total_cost']))}** instead of **{ru.precise_money(float(base54_medium['total_cost']))}**.
- More reasoning is not automatically better on this benchmark. `high` falls to **18/22**, `None` falls to **15/22**, and `xhigh` reaches only **17/22** while costing **{ru.precise_money(float(base54_xhigh['total_cost']))}**.
- `xhigh` is therefore not worth pursuing for baseline here: compared with `low`, it costs about **{ru.precise_money(float(base54_xhigh['total_cost'] - base54_low['total_cost']))} more** and solves **2 fewer** equations.
- `gpt-5.4-mini` is dominated by standard `gpt-5.4` on the current baseline sweep. At `low`, the standard model solves **19/22** for **{ru.precise_money(float(base54_low['total_cost']))}**, while mini solves only **10/22** for **{ru.precise_money(float(base_mini_low['total_cost']))}**.
- `gpt-5.4-nano` is the stronger lightweight baseline contender. At `medium` and `high`, nano reaches **16/22** and **17/22**, while mini reaches only **14/22** and **10/22**. A cautious interpretation is that nano responds much better than mini to explicit reasoning effort on this short proof benchmark.
"""

guided_md = f"""
## Guided

Guided search remains competitive, but it does not create a better frontier than baseline on the current report runs.

### Supported takeaways

- On `gpt-5.4`, guided reaches **18/22**, **19/22**, and **19/22** at `low`, `medium`, and `high`. That is very close to baseline's **19/22**, **19/22**, and **18/22** at the same effort levels.
- That similarity comes with a clear premium. Relative to baseline, guided costs about **{ru.precise_money(float(guided54_low['total_cost'] - base54_low['total_cost']))}** more at `low`, **{ru.precise_money(float(guided54_medium['total_cost'] - base54_medium['total_cost']))}** more at `medium`, and **{ru.precise_money(float(guided54_high['total_cost'] - base54_high['total_cost']))}** more at `high`.
- Higher reasoning effort in guided does not hurt solved count on `gpt-5.4`, but it still raises cost: `medium` and `high` both solve **19/22**, while `high` pays **{ru.precise_money(float(guided54_high['total_cost'] - guided54_medium['total_cost']))}** more.
- Guided does not rescue `gpt-5.4-mini`. Solved count stays flat at **12/22** while cost rises from **{ru.precise_money(float(guided_mini_low['total_cost']))}** at `low` to **{ru.precise_money(float(guided_mini_high['total_cost']))}** at `high`.
"""

step_md = f"""
## Step-by-Step

The new step-by-step runs are the strongest results in the report so far. They are not a full sweep yet, but they already change the overall conclusion.

### Supported takeaways

- The replicated `gpt-5.4` step executor with `low` reasoning effort is consistently strong. Across **{len(step_replicates)} runs** ({step_replicate_labels}), it solves between **{step_replicates_min_solved}** and **{step_replicates_max_solved}** equations for **{ru.precise_money(step_replicates_min_cost)}-{ru.precise_money(step_replicates_max_cost)}**.
- The best observed step-by-step run, **{best_step['experiment_name']}**, solves **22/22** equations for **{ru.precise_money(float(best_step['total_cost']))}**. That is both better than the best baseline run (**19/22**) and slightly cheaper than it.
- Within the currently available `gpt-5.4-mini` step runs, `low` is the sweet spot: it reaches **21/22** for **{ru.precise_money(float(step_mini_low['total_cost']))}**. `None` and `medium` are both worse and more expensive.
- `gpt-5.4-nano` with `low` is surprisingly competitive inside step-by-step: it also reaches **21/22** for **{ru.precise_money(float(step_nano_low['total_cost']))}**. `medium` keeps the same solved count but costs more, while `None` performs much worse.
- These step-by-step conclusions are still provisional because several cells in the intended sweep are missing. The current data is enough to identify a clear frontrunner, not to fully map the whole step-by-step landscape.
"""

three_way_md = f"""
## Three-Way Comparison

The strongest current runs are **{best_baseline['experiment_name']}**, **{best_guided['experiment_name']}**, and **{best_step['experiment_name']}**.

This comparison is the main result of the notebook. Baseline and guided top out at **19/22**, with guided paying a large premium. Step-by-step moves the frontier: it reaches full benchmark coverage while staying at essentially the same cost as the best baseline configuration.
"""

budget_md = f"""
The budget plot makes the three-way comparison easier to read.

- **Step-by-step reaches the top frontier**: it is the only current strategy that gets to **22 solved equations**.
- **It does so without a cost penalty**: the best step-by-step run ends at **{ru.precise_money(float(best_step['total_cost']))}**, versus **{ru.precise_money(float(best_baseline['total_cost']))}** for the best baseline run.
- **Guided remains the expensive option**: it matches baseline on solved count, but finishes about **{ru.precise_money(float(best_guided['total_cost'] - best_baseline['total_cost']))}** higher.
"""

step_difference_md = """
## What Step-by-Step Adds

A small benchmark-level check is worth keeping because it explains *where* the full-coverage result comes from.

The best step-by-step run solves two equations that both best baseline and best guided miss. It does not give up any equation that either of the other two best runs solves. That means the step-by-step win is a genuine expansion of coverage, not just a different trade.
"""

model_mistakes_md = f"""
## Common Failure Patterns by Model

The report artifacts do not record free-form error labels, so this section groups failures by the identity family of the missed benchmark. It is still useful because the patterns are sharp.

- `gpt-5.4` is narrow: its main weakness is **{gpt54_top['identity_family']}**, with **{int(gpt54_top['failures'])}/{int(gpt54_top['total'])}** failures (**{gpt54_top['failure_rate']:.1%}**). Outside that family it mostly slips on **{gpt54_second['identity_family']}**.
- `gpt-5.4-mini` is much broader in its misses. It struggles most on **{mini_top['identity_family']}** (**{int(mini_top['failures'])}/{int(mini_top['total'])}**, **{mini_top['failure_rate']:.1%}**), then on **{mini_second['identity_family']}**, and it still shows a substantial failure rate even on **{mini_third['identity_family']}**.
- `gpt-5.4-nano` looks closer to mini than to standard `gpt-5.4` in the kind of mistakes it makes, but it is more controlled. Its top two miss families are **{nano_top['identity_family']}** and **{nano_second['identity_family']}**, and its third most common miss family is **{nano_third['identity_family']}**.

Taken together, the most persistent weak spot across all three models is not the basic angle-shift or product-sum material, but the more derived identities built from multiple transformations, especially benchmarks `018` and `019`.
"""

missing_md = """
## Remaining Step-by-Step Cells

The current step-by-step evidence is already strong enough to include in the report, but the sweep is still incomplete. The missing runs below are the ones worth adding before making a firmer statement about reasoning-effort effects inside step-by-step itself.
"""

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}

cells = []
cells.append(md(intro_md))
cells.append(
    code(
        """
from pathlib import Path
import sys

import pandas as pd
from IPython.display import HTML, SVG, display

for candidate in [Path.cwd(), *Path.cwd().parents]:
    report_dir = candidate / 'examples' / 'mini_eqns' / 'experiments' / 'report'
    if report_dir.exists():
        REPORT_DIR = report_dir
        break
else:
    raise FileNotFoundError('Could not locate examples/mini_eqns/experiments/report from the current working directory.')

if str(REPORT_DIR) not in sys.path:
    sys.path.insert(0, str(REPORT_DIR))

import report_utils as ru

paths = ru.find_report_paths(Path.cwd())
benchmarks = ru.load_benchmarks(paths.benchmark_file)
runs = ru.load_report_runs(paths.report_root)
inventory = ru.build_experiment_inventory(runs)
best_configs = ru.select_best_configs(inventory)
best_baseline_name = str(best_configs.loc[best_configs['family'] == 'baseline', 'experiment_name'].iloc[0])
best_guided_name = str(best_configs.loc[best_configs['family'] == 'guided', 'experiment_name'].iloc[0])
best_step_name = str(best_configs.loc[best_configs['family'] == 'step_by_step', 'experiment_name'].iloc[0])
step_advantage = ru.build_step_advantage_table(runs, benchmarks, best_baseline_name, best_guided_name, best_step_name)

pd.set_option('display.max_colwidth', 120)
display(HTML('''
<style>
.jp-RenderedMarkdown {
  max-width: 920px;
  margin: 0 auto;
  line-height: 1.55;
}
.jp-RenderedMarkdown h1 { font-size: 1.75rem; margin-top: 0.15rem; margin-bottom: 0.55rem; }
.jp-RenderedMarkdown h2 { font-size: 1.22rem; margin-top: 1.35rem; margin-bottom: 0.4rem; }
.jp-RenderedMarkdown h3 { font-size: 1.02rem; margin-top: 0.95rem; margin-bottom: 0.28rem; }
.jp-RenderedMarkdown p, .jp-RenderedMarkdown li { font-size: 0.97rem; }
.table-container, .strategy-wrap { max-width: 920px; margin: 0 auto; }
.report-simple-table, .strategy-matrix {
  border-collapse: collapse;
  width: 100%;
  font-size: 13px;
  margin: 0.35rem 0 0.8rem 0;
}
.report-simple-table th, .report-simple-table td, .strategy-matrix th, .strategy-matrix td {
  border-bottom: 1px solid #e5e7eb;
  padding: 8px 10px;
  text-align: left;
  vertical-align: middle;
}
.report-simple-table th, .strategy-matrix th {
  background: #f8fafc;
  font-weight: 600;
}
.strategy-matrix td.empty {
  color: #94a3b8;
  text-align: center;
}
.matrix-card {
  border-radius: 10px;
  padding: 10px 10px 8px 10px;
  min-width: 108px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.45);
}
.matrix-card .solve { font-size: 16px; font-weight: 700; line-height: 1.1; }
.matrix-card .cost { font-size: 12px; margin-top: 4px; }
.matrix-card .label { font-size: 11px; margin-top: 6px; opacity: .82; }
</style>
'''))
"""
    )
)
cells.append(md(method_md))
cells.append(md(baseline_md))
cells.append(code("display(HTML(ru.render_strategy_matrix_html(inventory, 'baseline')))"))
cells.append(md(guided_md))
cells.append(code("display(HTML(ru.render_strategy_matrix_html(inventory, 'guided')))"))
cells.append(md(step_md))
cells.append(code("display(HTML(ru.render_step_by_step_matrix_html(inventory)))"))
cells.append(md(three_way_md))
cells.append(
    code(
        """
leaderboard = inventory.loc[
    inventory['experiment_name'].isin([best_baseline_name, best_guided_name, best_step_name]),
    ['family', 'experiment_name', 'model_name', 'reasoning_effort', 'sketch_model_name', 'sketch_reasoning_effort', 'solved', 'total_cost']
].copy()
leaderboard['strategy'] = leaderboard['family'].map({
    'baseline': 'Baseline',
    'guided': 'Guided',
    'step_by_step': 'Step-by-step',
})
leaderboard['executor'] = leaderboard['model_name'].map(ru.model_label)
leaderboard['executor effort'] = leaderboard['reasoning_effort'].astype(str)
leaderboard['sketch'] = leaderboard.apply(
    lambda row: f"{ru.model_label(str(row['sketch_model_name']))} / {row['sketch_reasoning_effort']}" if row['family'] == 'step_by_step' else '—',
    axis=1,
)
leaderboard = leaderboard[['strategy', 'experiment_name', 'executor', 'executor effort', 'sketch', 'solved', 'total_cost']]
leaderboard = leaderboard.sort_values(['solved', 'total_cost'], ascending=[False, True])
leaderboard = leaderboard.rename(columns={
    'experiment_name': 'experiment',
    'solved': 'solved',
    'total_cost': 'total cost',
})
display(HTML(ru.render_simple_table_html(
    leaderboard,
    formatters={
        'solved': lambda value: f'{int(value)}/22',
        'total cost': ru.precise_money,
    },
)))
"""
    )
)
cells.append(
    code(
        """
curves = ru.load_budget_curves(paths.report_root, [best_baseline_name, best_guided_name, best_step_name])
display(SVG(ru.render_budget_curves_svg(curves, inventory, title='Budget curves for the best current runs')))
"""
    )
)
cells.append(md(budget_md))
cells.append(md(step_difference_md))
cells.append(
    code(
        """
step_only = step_advantage.loc[step_advantage['status'] == 'step_only', ['bench_name', 'equation', 'baseline', 'guided', 'step_by_step']].copy()
step_only = step_only.rename(columns={
    'baseline': 'best baseline',
    'guided': 'best guided',
    'step_by_step': 'best step-by-step',
})
display(HTML(ru.render_simple_table_html(
    step_only,
    formatters={
        'best baseline': lambda value: 'yes' if value else 'no',
        'best guided': lambda value: 'yes' if value else 'no',
        'best step-by-step': lambda value: 'yes' if value else 'no',
    },
)))
print(f'Step regressions against the best baseline/guided runs: {int((step_advantage["status"] == "step_regression").sum())}')
"""
    )
)
cells.append(md(model_mistakes_md))
cells.append(
    code(
        """
BENCHMARK_GROUPS = {
    '001': 'phase shifts', '002': 'phase shifts', '003': 'phase shifts', '004': 'phase shifts',
    '005': 'special angles', '006': 'special angles', '007': 'special angles',
    '008': 'periodicity', '009': 'periodicity',
    '010': 'pythagorean',
    '011': 'double-angle / half-angle', '012': 'sum-product transforms', '013': 'sum-product transforms',
    '014': 'double-angle / half-angle', '015': 'double-angle / half-angle', '016': 'double-angle / half-angle', '017': 'double-angle / half-angle',
    '018': 'derived product identities', '019': 'derived product identities',
    '020': 'higher-order sine rewrites', '021': 'higher-order sine rewrites', '022': 'higher-order sine rewrites',
}

model_runs = runs.copy()
model_runs['analysis model'] = model_runs['model_name'].astype(str)
step_mask = model_runs['family'] == 'step_by_step'
model_runs.loc[step_mask, 'analysis model'] = model_runs.loc[step_mask, 'step_model_name'].astype(str)
model_runs['identity family'] = model_runs['bench_name'].map(BENCHMARK_GROUPS)
model_runs['failed'] = ~model_runs['success']
summary = (
    model_runs.groupby(['analysis model', 'identity family'], dropna=False)
    .agg(failures=('failed', 'sum'), total=('failed', 'size'))
    .reset_index()
)
summary['failure rate'] = summary['failures'] / summary['total']
summary = summary.sort_values(['analysis model', 'failure rate', 'failures', 'identity family'], ascending=[True, False, False, True])
ranked = summary.groupby('analysis model').head(3).copy()
ranked['family'] = ranked['identity family']
ranked['evidence'] = ranked.apply(lambda row: f"{int(row['failures'])}/{int(row['total'])} ({row['failure rate']:.1%})", axis=1)
ranked = ranked[['analysis model', 'family', 'evidence']].rename(columns={'analysis model': 'model'})
display(HTML(ru.render_simple_table_html(ranked)))
"""
    )
)
cells.append(md(missing_md))
cells.append(
    code(
        """
missing_step = ru.build_step_missing_table(inventory)
missing_step = missing_step.loc[missing_step['status'] == 'missing'].copy()
display(HTML(ru.render_simple_table_html(missing_step)))
"""
    )
)

nb["cells"] = cells
NOTEBOOK_PATH.write_text(nbf.writes(nb))

try:
    from nbclient import NotebookClient
except Exception as exc:
    print(f'Wrote {NOTEBOOK_PATH} but could not execute it automatically: {exc}')
else:
    executed = nbf.read(NOTEBOOK_PATH, as_version=4)
    client = NotebookClient(executed, timeout=600, kernel_name='python3')
    client.execute()
    NOTEBOOK_PATH.write_text(nbf.writes(executed))
    print(f'Wrote and executed {NOTEBOOK_PATH}')
