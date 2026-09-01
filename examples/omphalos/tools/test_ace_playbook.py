"""
Unit test for `ace_playbook` (pure Python — no LLM, no Rocq).

Run `python tools/test_ace_playbook.py` (from any cwd). Exercises:

  1. id assignment, counter updates, unknown-tag warning;
  2. dedup: exact normalized match and a near-verbatim variant fold
     into the existing bullet (helpful += 1) instead of growing;
  3. distinct content in the *same* section is kept; identical content
     in a *different* section is kept (dedup is per-section);
  4. size guard: an ADD that would exceed `max_tokens` is dropped
     deterministically and recorded;
  5. YAML round-trip preserves content and `sha256` exactly, and the
     hash changes when the playbook changes;
  6. merge never mutates its input;
  7. markdown rendering is stable and groups by section in
     first-appearance order.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ace_playbook import (  # noqa: E402
    AddOp,
    BulletTag,
    Playbook,
    merge,
)


def _add(section: str, content: str) -> AddOp:
    return AddOp(type="ADD", section=section, content=content)


def main() -> None:
    pb = Playbook()

    # 1. Fresh adds get sequential ids; tags on unknown ids warn.
    out = merge(
        pb,
        [
            _add("pitfalls", "Bridge `S n` vs `n + 1` with lia."),
            _add("tactics", "Use nra for nonlinear real goals."),
        ],
        [BulletTag(id="rocq-99999", tag="helpful")],
    )
    assert out.added == ["rocq-00001", "rocq-00002"], out.added
    assert out.playbook.next_id == 3
    assert len(out.warnings) == 1 and "unknown" in out.warnings[0]
    assert pb.bullets == [] and pb.next_id == 1  # 6. input untouched

    # 1b. Counter updates on known ids.
    out2 = merge(
        out.playbook,
        [],
        [
            BulletTag(id="rocq-00001", tag="helpful"),
            BulletTag(id="rocq-00001", tag="harmful"),
            BulletTag(id="rocq-00002", tag="neutral"),
        ],
    )
    b1 = out2.playbook.bullets[0]
    assert (b1.helpful, b1.harmful) == (1, 1)
    b2 = out2.playbook.bullets[1]
    assert (b2.helpful, b2.harmful) == (0, 0)  # neutral: no counter

    # 2. Dedup: exact normalized + near-verbatim variants fold in.
    out3 = merge(
        out2.playbook,
        [
            _add("pitfalls", "bridge `s n` vs `n + 1`  with lia"),
            _add("pitfalls", "Bridge `S n` vs `n + 1` with lia first."),
        ],
        [],
    )
    assert out3.added == []
    assert [d[0] for d in out3.deduped] == ["rocq-00001", "rocq-00001"]
    assert out3.playbook.bullets[0].helpful == 3  # 1 tag + 2 dedups
    assert out3.playbook.next_id == 3  # no id burned on duplicates

    # 3. Same section, different content -> kept; same content in a
    #    different section -> kept (dedup is per-section).
    out4 = merge(
        out3.playbook,
        [
            _add("pitfalls", "Name every hypothesis you introduce."),
            _add("strategy", "Use nra for nonlinear real goals."),
        ],
        [],
    )
    assert out4.added == ["rocq-00003", "rocq-00004"]

    # 4. Size guard drops deterministically.
    out5 = merge(
        out4.playbook,
        [_add("strategy", "x" * 4000)],
        [],
        max_tokens=out4.playbook.token_estimate() + 10,
    )
    assert out5.added == [] and out5.dropped == ["x" * 4000]
    assert out5.playbook.next_id == out4.playbook.next_id
    assert any("size guard" in w for w in out5.warnings)

    # 5. Round-trip + hash stability.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pb.yaml"
        out4.playbook.save(path)
        reloaded = Playbook.load(path)
        assert reloaded == out4.playbook
        assert reloaded.sha256() == out4.playbook.sha256()
    changed = merge(out4.playbook, [_add("strategy", "New fact.")], [])
    assert changed.playbook.sha256() != out4.playbook.sha256()

    # 7. Rendering: sections in first-appearance order, ids visible.
    md = out4.playbook.render_markdown()
    assert md.index("### pitfalls") < md.index("### tactics")
    assert md.index("### tactics") < md.index("### strategy")
    assert "[rocq-00001] (helpful=3, harmful=1)" in md
    assert Playbook().render_markdown() == "(the playbook is empty so far)"

    print("test_ace_playbook: all assertions passed")


if __name__ == "__main__":
    main()
