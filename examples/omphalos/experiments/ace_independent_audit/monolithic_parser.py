"""Opt-in repair for the observed monolithic YAML serialization defect.

Valid YAML is consumed unchanged. Only a YAML syntax failure permits quoting
unquoted single-line `content` scalars; the full typed schema must still
validate. This never edits an archived reply or replay result and is not
installed into a sealed historical query.
"""

from dataclasses import asdict
import json
import re
from typing import Any

from delphyne.stdlib.queries import extract_final_block
from pydantic import TypeAdapter
import yaml

from prove_ace import PlaybookRewrite

from .analysis import historical
from .audit import load_yaml
from .common import REPORT, ROOT, digest, save, sha
from .learning_v3 import outer_yaml

SCHEMA = TypeAdapter(PlaybookRewrite)


def quote_content_scalars(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(\s*(?:-\s+)?content:\s*)(\S.*)$", line)
        if match and match[2][0] not in "|>'\"[{&*!#":
            line = match[1] + json.dumps(match[2], ensure_ascii=False)
        lines.append(line)
    return "\n".join(lines) + "\n"


def parse_rewrite(text: str) -> PlaybookRewrite:
    body = outer_yaml(text)
    try:
        value = yaml.safe_load(body)
    except yaml.YAMLError:
        value = yaml.safe_load(quote_content_scalars(body))
    return SCHEMA.validate_python(value)


def run() -> None:
    rows = [
        r
        for r in historical()
        if r["config"]["strategy"] == "rewrite_playbook"
    ]
    if len(rows) != 80:
        raise ValueError(
            "Historical monolithic diagnostic denominator changed"
        )
    replies: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    for row in rows:
        path = ROOT / row["path"] / "cache.yaml"
        if sha(path) != row["cache_sha"]:
            raise ValueError("Historical monolithic cache changed")
        original_usable = repaired_usable = False
        for index, record in enumerate(load_yaml(path)):
            output: dict[str, Any] = record.get("output") or {}
            if output.get("model_name") == "__compute__":
                continue
            for reply in output.get("outputs", []):
                text = reply["content"]
                old: PlaybookRewrite | None = None
                try:
                    block = extract_final_block(text)
                    if block is not None:
                        old = SCHEMA.validate_python(yaml.safe_load(block))
                except (ValueError, yaml.YAMLError):
                    pass
                new = parse_rewrite(text)
                if old is not None and old != new:
                    raise ValueError("Repair changed a previously valid value")
                original_usable |= old is not None
                repaired_usable = True
                replies.append(
                    dict(
                        path=row["path"],
                        cache_index=index,
                        raw_sha=digest(text),
                        originally_valid=old is not None,
                        repaired_valid=True,
                        parsed_sha=digest(asdict(new)),
                    )
                )
        cells.append(
            dict(
                path=row["path"],
                originally_usable=original_usable,
                repaired_usable=repaired_usable,
            )
        )
    result = dict(
        cells=len(cells),
        replies=len(replies),
        originally_valid=sum(r["originally_valid"] for r in replies),
        repaired_valid=len(replies),
        original_usable_cells=sum(r["originally_usable"] for r in cells),
        repaired_usable_cells=sum(r["repaired_usable"] for r in cells),
        common_valid_values_unchanged=True,
        paid_calls=0,
        observations=replies,
        cell_outcomes=cells,
        limitation="This validates a serialization repair on saved replies. It does not reconstruct the different future prompts of an adaptively repaired monolithic learner or claim a solver coverage gain.",
    )
    save(REPORT / "monolithic_parser_certification.json", result)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ("observations", "cell_outcomes")
            }
        )
    )


if __name__ == "__main__":
    run()
