"""Build opt-in role demos from the recorded, real-Rocq offline exercise.

Both harnesses: python -m tools.data.writer_draft_demos. No API calls.
The example family is excluded from evaluation queries by draft_examples.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from copy import deepcopy
import json
from typing import Any

import yaml

from experiments import writer_draft_experiment as c


def main() -> None:
    source = yaml.safe_load(
        (c.ROOT / "demos/reducer_snippets.study.demo.yaml").read_text()
    )[0]
    demos: list[dict[str, Any]] = []
    for role in ("curator", "reducer"):
        item = deepcopy(source)
        item["demonstration"] = role + "_repairs_unverified_draft"
        item["query"] = "WriteRocqDraftAdvice"
        item["args"]["role"] = role
        raw = json.loads(item["args"]["evidence"])["unverified_candidates"][0]
        raw.pop("status")
        raw.update(
            error="Historical Rocq syntax error in have", remaining_goals=[]
        )
        item["args"]["drafts"] = [raw]
        answer = yaml.safe_load(
            item["answers"][0]["answer"]
            .removeprefix("```yaml\n")
            .removesuffix("```")
        )
        answer["decisions"] = [
            dict(
                draft_id=raw["draft_id"],
                action="retain",
                reason="The empty demonstration book lacks the square bridge; exact repaired syntax is checked in its source.",
                receipts=answer["retained_receipts"],
            )
        ]
        item["answers"][0]["answer"] = (
            "```yaml\n" + yaml.safe_dump(answer, sort_keys=False) + "```"
        )
        demos.append(item)
    (c.ROOT / "demos/writer_drafts.demo.yaml").write_text(
        yaml.safe_dump(demos, sort_keys=False, width=79)
    )


if __name__ == "__main__":
    main()
