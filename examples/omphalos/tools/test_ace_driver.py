"""
Unit tests for the ACE adaptation driver's pure parts and its store.

Pure Python — no LLM, no Rocq, no experiment directories: the driver's
`execute` is exercised with stub role runners that return canned
Reflector/Curator outputs written as `result.yaml` files into a
temporary tree. Part of `make test-unit`.

Covers the defects the 2026-08-25 audit found: batched steps consuming
a playbook file that did not exist yet (content addressing), stale
step files from a longer earlier run (index pruning), identical
traversal order across epochs (seeded shuffle), a placeholder rendering
at step 0 (v2 renders ""), a deduper that never fires (Jaccard), and
counters that gated nothing (refine prunes).
"""

# pyright: strict

import sys
import tempfile
from pathlib import Path
from typing import Any, cast

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

import ace_store  # noqa: E402
from ace_dedup import JaccardDeduper, LexicalDeduper  # noqa: E402
from ace_playbook import (  # noqa: E402
    AddOp,
    BulletTag,
    Playbook,
    merge,
    refine,
)


def _pb(*contents: str, section: str = "tactics") -> Playbook:
    pb = Playbook()
    for c in contents:
        pb = merge(
            pb, [AddOp(type="ADD", section=section, content=c)], []
        ).playbook
    return pb


def test_render_prompt() -> None:
    assert Playbook().render_prompt() == ""
    pb = _pb("Use `nra` on nonlinear real goals.")
    pb.bullets[0].helpful = 3
    md = pb.render_prompt()
    assert "[rocq-00001] Use `nra`" in md
    assert "helpful" not in md and "harmful" not in md
    # v1 rendering is untouched.
    assert "(helpful=3, harmful=0)" in pb.render_markdown()


def test_jaccard_fires_where_lexical_does_not() -> None:
    a = "For nonlinear goals over R, call `nra` after `unfold Rsqr`."
    b = "Call `nra` on nonlinear R goals once `Rsqr` is unfolded with `unfold Rsqr`."
    pb = _pb(a)
    op = AddOp(type="ADD", section="tactics", content=b)
    lex = merge(pb, [op], [], deduper=LexicalDeduper())
    assert lex.added == ["rocq-00002"], (
        "lexical rule should not fold a paraphrase"
    )
    jac = merge(
        pb, [op], [], deduper=JaccardDeduper(), dedup_counts_helpful=False
    )
    assert jac.added == [] and jac.deduped[0][0] == "rocq-00001"
    assert jac.playbook.bullets[0].helpful == 0, (
        "a fold must not count as helpful"
    )


def test_refine_prunes_and_merges() -> None:
    pb = _pb(
        "Bridge `S n` with `n + 1` using `replace (S n) with (n + 1) by lia`.",
        "Use `replace (S n) with (n + 1) by lia` to bridge `S n` and `n + 1`.",
        "Guess lemma names freely.",
        "Prefer `field_simplify` before `nra` on fractions.",
    )
    pb = merge(
        pb,
        [],
        [
            BulletTag(id="rocq-00003", tag="harmful"),
            BulletTag(id="rocq-00003", tag="harmful"),
            BulletTag(id="rocq-00004", tag="harmful"),  # once: noise, kept
            BulletTag(id="rocq-00002", tag="helpful"),
        ],
    ).playbook
    out = refine(pb, JaccardDeduper(), prune_harmful=True)
    assert [b.id for b in out.pruned] == ["rocq-00003"]
    assert [m[:2] for m in out.merged] == [("rocq-00001", "rocq-00002")]
    kept = {b.id: b for b in out.playbook.bullets}
    assert set(kept) == {"rocq-00001", "rocq-00004"}
    assert kept["rocq-00001"].helpful == 1, (
        "counters are summed into the survivor"
    )
    assert out.playbook.next_id == pb.next_id, "ids are never reused"
    assert len(pb.bullets) == 4, "refine never mutates its input"
    again = refine(out.playbook, JaccardDeduper(), prune_harmful=True)
    assert again.playbook == out.playbook, "refine is idempotent"


def test_refine_compacts_lowest_score_first() -> None:
    pb = _pb("A" * 200, "B" * 200, "C" * 200)
    pb.bullets[0].helpful = 2
    pb.bullets[2].helpful = 1
    out = refine(
        pb,
        LexicalDeduper(),
        prune_harmful=False,
        max_tokens=pb.token_estimate() - 60,
    )
    assert [b.id for b in out.compacted] == ["rocq-00002"]


def test_store_is_content_addressed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ace_store.PLAYBOOKS_DIR = Path(tmp)
        store = ace_store.PlaybookStore("unit")
        pb0, pb1 = Playbook(), _pb("x")
        s0, s1 = store.put(pb0), store.put(pb1)
        assert s0 != s1 and store.get(s1) == pb1
        assert store.put(pb1) == s1, "put is idempotent"
        # Index derivation prunes stale files from a longer earlier run.
        store.write_step_index([s0, s1, s1, s1])
        assert store.step_path(3).exists()
        store.write_step_index([s0, s1])
        assert (
            not store.step_path(2).exists() and not store.step_path(3).exists()
        )
        assert Playbook.load(store.step_path(1)) == pb1
        # Legacy materialisation is idempotent.
        _pb("legacy").save(store.step_path(5))
        assert store.materialize_legacy_steps() == 1
        assert store.materialize_legacy_steps() == 0


def test_plan_and_shuffle() -> None:
    import ace_adaptation as ad

    order = list(ad.POOLS["train"])
    assert ad.order_for_epoch(order, 0, None) == order
    e0 = ad.order_for_epoch(order, 0, 7)
    e1 = ad.order_for_epoch(order, 1, 7)
    assert sorted(e0) == sorted(order) and sorted(e1) == sorted(order)
    assert e0 != e1 and e0 != order
    assert ad.order_for_epoch(order, 1, 7) == e1, "deterministic"

    v = ad.AdaptVariant(
        "unit-b4", "train", "unit.yaml", batch_size=4, epochs=2, shuffle_seed=3
    )
    batches = ad.plan(v, 2, None)
    assert len(batches) == 10 and all(len(b) == 4 for b in batches)
    steps = [s for b in batches for s in b]
    assert [s.step for s in steps] == list(range(40))
    assert steps[20].epoch == 1 and steps[20].pos_in_epoch == 0
    assert all(s.batch_id == i // 4 for i, s in enumerate(steps))
    assert (
        len(ad.plan(v, 2, 5)) == 2
        and sum(len(b) for b in ad.plan(v, 2, 5)) == 5
    )

    online = ad.AdaptVariant("unit-on", "validationX", None, mode="online")
    ob = ad.plan(online, 1, None)
    assert [s.bench for b in ob for s in b] == list(ad.POOLS["validationX"])


def test_variant_table_invariants() -> None:
    import ace_adaptation as ad

    legacy = ad.VARIANTS["train"]
    assert legacy.render_version == 1 and legacy.dedup == "lexical"
    assert legacy.refine_every == 0 and legacy.count_dedup_as_helpful
    for name, v in ad.VARIANTS.items():
        if name.startswith("x-"):
            assert v.render_version == 2 and v.curator_contract == 2
            assert v.show_definitions and v.dedup == "embedding"
            assert v.generator_cap == ad.x.X_DOLLAR_CAP
        assert v.name == name
    assert ad.VARIANTS["x-online-s1"].seed == 1
    assert (
        ad.VARIANTS["x-online-warm-s0"].warmup_playbook == "ace_x_offline.yaml"
    )


def test_v3_variant_invariants() -> None:
    import ace_adaptation as ad

    for name, v in ad.VARIANTS.items():
        if not name.startswith("x3-"):
            continue
        assert v.render_version == 3 and v.curator_contract == 3, name
        assert v.show_definitions and v.dedup == "embedding", name
        if v.reduce_batch:
            assert v.batch_size > 1 and v.curator_mode == "incremental", name
    assert ad.VARIANTS["x3-offline"].batch_size == 4
    assert ad.VARIANTS["x3-gate-b1"].batch_size == 1
    assert ad.VARIANTS["x3-offline-e3"].playbook_max_tokens == 8000
    assert ad.VARIANTS["x3-mono"].batch_size == 1, "monolithic must not batch"
    # legacy families untouched
    assert ad.VARIANTS["train"].curator_contract == 1
    assert ad.VARIANTS["x-offline"].curator_contract == 2


def test_section_whitelist() -> None:
    from ace_playbook import AddOp, Playbook, merge

    out = merge(
        Playbook(),
        [
            AddOp(type="ADD", section="Lemmas", content="a"),
            AddOp(type="ADD", section="hallucinated_section", content="b"),
        ],
        [],
    )
    assert [b.section for b in out.playbook.bullets] == ["lemmas", "strategy"]
    assert any("rerouted" in w for w in out.warnings)


def test_step_config_identity_is_backward_compatible() -> None:
    """Defaulted fields must not enter a legacy config's identity."""
    import ace_adaptation as ad
    from delphyne.stdlib.experiments.experiment_launcher import (
        _config_unique_repr,  # pyright: ignore[reportPrivateUsage]
    )

    cfg = ad.ACEAdaptStepConfig(
        role="generator",
        step=0,
        bench_name="x",
        seed=0,
        model_name="m",
        toolset="core",
        reasoning_effort="medium",
        num_requests=32,
        max_dollar_budget=0.05,
        playbook_sha256="abc",
    )
    rep = _config_unique_repr(cfg)
    for absent in (
        "api",
        "render_version",
        "curator_contract",
        "generator_dir",
        "show_definitions",
        "max_new_bullets",
        "injection",
        # v5 (2026-09-02)
        "reducer_contract",
        "evidence",
        "known_guidance",
        "references",
        "environments",
        "provenance",
        "audit_max_additions",
    ):
        assert f'"{absent}"' not in rep, absent


def test_cited_bullet_ids_assistant_only() -> None:
    """Ids in the system prompt, feedback and tool results never count."""
    import yaml

    import ace_adaptation as ad

    entry: dict[str, Any] = {
        "input": {
            "request": {
                "chat": [
                    {
                        "role": "system",
                        "content": "- [rocq-00001] a\n- [rocq-00002] b",
                    },
                    {"role": "user", "content": "Theorem t : True."},
                    {
                        "role": "assistant",
                        "answer": {
                            "mode": "text",
                            "content": "I rely on [rocq-00002] and rocq-00009.",
                        },
                    },
                    {
                        "role": "user",
                        "is_feedback": True,
                        "content": "see [rocq-00001]",
                    },
                    {
                        "role": "tool",
                        "call": {"name": "SearchRocq", "args": {}},
                        "result": "[rocq-00003]",
                    },
                ]
            }
        },
        "output": {"outputs": [{"content": "Also [rocq-00001] now."}]},
    }
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "cache.yaml").write_text(yaml.safe_dump([entry]))
        ids = ad.cited_bullet_ids(
            d, "t", {"rocq-00001", "rocq-00002", "rocq-00003"}
        )
        assert ids == ["rocq-00002", "rocq-00001"], ids
        traj = ad.extract_trajectory(d, "t")
        assert traj.startswith("[PROBLEM]\nTheorem t : True.")
        assert traj.endswith("[ASSISTANT]\nAlso [rocq-00001] now.")


def test_render_cited_subset_and_empty() -> None:
    from ace_bench import render_cited

    pb = Playbook()
    pb = merge(
        pb,
        [
            AddOp("ADD", "tactics", "use nia"),
            AddOp("ADD", "lemmas", "Rsqr_sqrt"),
        ],
        [],
    ).playbook
    ids = [b.id for b in pb.bullets]
    text = render_cited(pb, [ids[1]], 3)
    assert text.startswith(
        "Only the bullets the generator cited are shown (1 of 2)"
    )
    assert ids[1] in text and ids[0] not in text
    assert render_cited(pb, [], 3) == "(the generator cited no bullets)"
    assert (
        render_cited(pb, ["rocq-99999"], 3)
        == "(the generator cited no bullets)"
    )


def test_x4_is_a_minimal_pair_of_x3() -> None:
    from dataclasses import asdict

    import ace_adaptation as ad

    a = asdict(ad.VARIANTS["x3-offline"])
    b = asdict(ad.VARIANTS["x4-offline"])
    diff = {k for k in a if a[k] != b[k]}
    assert diff == {"name", "final_playbook", "reflector_scope"}, diff
    assert b["reflector_scope"] == "cited"
    a = asdict(ad.VARIANTS["x3-online-s0"])
    b = asdict(ad.VARIANTS["x4-online-s0"])
    assert {k for k in a if a[k] != b[k]} == {"name", "reflector_scope"}


def test_x3_strong_is_a_minimal_pair_of_x3() -> None:
    """Role strength alone: model on the reflector + curation side, and
    the cap that keeps terra's calls from being truncated."""
    from dataclasses import asdict

    import ace_adaptation as ad

    a = asdict(ad.VARIANTS["x3-offline"])
    b = asdict(ad.VARIANTS["x3-strong"])
    diff = {k for k in a if a[k] != b[k]}
    assert diff == {
        "name",
        "final_playbook",
        "reflector_model",
        "curator_model",
        "role_cap",
    }, diff
    strong = ad.VARIANTS["x3-strong"]
    for role in ("reflector", "curator", "reducer", "grounder", "auditor"):
        assert strong.role_model(role) == "gpt-5.6-terra", role
        assert strong.role_effort(role) == ad.ADAPT_EFFORT, role
    assert strong.role_model("generator") == ad.ADAPT_MODEL
    base = ad.VARIANTS["x3-offline"]
    assert base.role_model("reducer") == ad.ADAPT_MODEL
    assert base.role_cap == ad.ROLE_DOLLAR_CAP


def test_role_effort_and_cap_reach_the_step_config() -> None:
    import ace_adaptation as ad

    v = ad.VARIANTS["x3-strong"]
    s = ad.StepPlan(0, 0, 0, next(iter(ad.POOLS[v.pool])), 0)
    refl = ad._make_step_config(  # pyright: ignore[reportPrivateUsage]
        v, "reflector", s, "sha"
    )
    assert refl.model_name == "gpt-5.6-terra"
    assert refl.max_dollar_budget == 0.25
    assert refl.reasoning_effort == ad.ADAPT_EFFORT
    gen = ad._make_step_config(  # pyright: ignore[reportPrivateUsage]
        v, "generator", s, "sha"
    )
    assert gen.model_name == ad.ADAPT_MODEL
    assert gen.max_dollar_budget == v.generator_cap
    # An x3 config is unchanged by the plumbing (same identity as before).
    v3 = ad.VARIANTS["x3-offline"]
    r3 = ad._make_step_config(  # pyright: ignore[reportPrivateUsage]
        v3, "reducer", s, "sha"
    )
    assert r3.model_name == ad.ADAPT_MODEL
    assert r3.max_dollar_budget == ad.ROLE_DOLLAR_CAP
    assert r3.reasoning_effort == ad.ADAPT_EFFORT


def test_x5_bundle_is_exactly_the_declared_knobs() -> None:
    """x5-offline is x3-offline plus the v5 mechanisms and nothing else."""
    from dataclasses import asdict

    import ace_adaptation as ad

    a = asdict(ad.VARIANTS["x3-offline"])
    b = asdict(ad.VARIANTS["x5-offline"])
    diff = {k for k in a if a[k] != b[k]}
    assert diff == {
        "name",
        "final_playbook",
        "curator_contract",
        "reducer_contract",
        "grounding",
        "skip_trivial",
        "audit",
        "preaudit_playbook",
    }, diff
    v = ad.VARIANTS["x5-offline"]
    assert v.render_version == 3, "the Generator prompt stays at v3"
    assert v.role_model("auditor") == ad.ADAPT_MODEL
    # Every recorded variant keeps the v5 mechanisms off.
    for name, other in ad.VARIANTS.items():
        if not name.startswith("x5-"):
            assert not (other.grounding or other.audit), name
            assert other.reducer_contract == 1 and not other.skip_trivial, name


def test_recorded_curator_delta_still_parses() -> None:
    """`AddOp.references` is defaulted: a v3 curator's cached YAML
    (no `references` key) must still load."""
    import ace_adaptation as ad

    recorded = (
        Path(__file__).resolve().parent.parent
        / "experiments/output/ace_adaptation_x3-offline/configs"
        / "step35_curator_amc12b_2003_p17"
    )
    if not recorded.exists():
        print(
            "  (no recorded x3-offline curator on disk; parse check skipped)"
        )
        return
    delta = ad.load_delta(recorded)
    assert delta is not None and delta.operations
    assert all(op.references == [] for op in delta.operations)
    gen = recorded.parent / "step35_generator_amc12b_2003_p17"
    assert ad.read_requests(gen) >= 1


def test_grounding_gate() -> None:
    import ace_adaptation as ad
    from prove_ace import GroundingResult

    a = AddOp(
        type="ADD", section="lemmas", content="a", references=["pow2_sqrt"]
    )
    b = AddOp(
        type="ADD",
        section="lemmas",
        content="b",
        references=["norm_num", "lia"],
    )
    c = AddOp(
        type="ADD", section="tactics", content="c", references=["Weird_name"]
    )
    d = AddOp(type="ADD", section="tactics", content="d", references=[])
    results = [
        GroundingResult("pow2_sqrt", "grounded", "f.v", "Constant …"),
        GroundingResult(
            "norm_num", "missing", "f.v", "No object of basename norm_num"
        ),
        GroundingResult(
            "Weird_name", "error", "f.v", "Rocq rejected the command: x"
        ),
    ]
    gate = ad._apply_gate([a, b, c, d], results)  # pyright: ignore[reportPrivateUsage]
    assert gate.keep([a, b, c, d]) == [a, c, d]
    assert gate.refused == {id(b): ["norm_num"]}
    assert gate.errors == {id(c)}
    # Grounder failed entirely: keep everything, count what was uncheckable.
    none_gate = ad._apply_gate([a, b, d], None)  # pyright: ignore[reportPrivateUsage]
    assert none_gate.keep([a, b, d]) == [a, b, d]
    assert none_gate.errors == {id(a), id(b)}


def test_attribute_and_provenance() -> None:
    import ace_adaptation as ad

    ops = [
        AddOp(type="ADD", section="lemmas", content="one", references=["x"]),
        AddOp(type="ADD", section="lemmas", content="dup", references=[]),
        AddOp(type="ADD", section="tactics", content="three", references=[]),
    ]
    pairs = ad._attribute(  # pyright: ignore[reportPrivateUsage]
        ops, ["rocq-00007", "rocq-00008"], ["dup"]
    )
    assert pairs == [("rocq-00007", ops[0]), ("rocq-00008", ops[2])]
    pb = _pb("one", "three", section="lemmas")
    pb.bullets[0].helpful = 2
    prov = {
        "rocq-00001": ad._provenance_record(  # pyright: ignore[reportPrivateUsage]
            ops[0], 3, ["amc12_2000_p1"], [True], "curator"
        )
    }
    block = ad._provenance_block(pb, prov)  # pyright: ignore[reportPrivateUsage]
    lines = block.split("\n")
    assert lines[0].startswith(
        "- [rocq-00001] step 3 (curator), from amc12_2000_p1 (solved)"
    )
    assert "helpful=2, harmful=0; references: x" in lines[0]
    assert (
        lines[1] == "- [rocq-00002] origin not recorded; helpful=0, harmful=0"
    )


def test_grounder_and_auditor_configs() -> None:
    import ace_adaptation as ad

    v = ad.VARIANTS["x5-offline"]
    s = ad.StepPlan(4, 0, 4, "mathd_algebra_28", 1)
    cfg = ad._make_step_config(  # pyright: ignore[reportPrivateUsage]
        v,
        "grounder",
        s,
        "sha",
        references="pow2_sqrt\nNat.div_mod_eq",
        environments="a.v@t|b.v@u",
    )
    name = ad._config_name(  # pyright: ignore[reportPrivateUsage]
        cfg,
        ad._NO_UID,  # pyright: ignore[reportPrivateUsage]
    )
    assert name == "step04_grounder_mathd_algebra_28"
    args = cfg.instantiate(None)
    assert args.strategy == "ground_references"
    assert args.args == {
        "names": ["pow2_sqrt", "Nat.div_mod_eq"],
        "environments": [("a.v", "t"), ("b.v", "u")],
    }
    final = ad.StepPlan(40, 0, 0, ad.AUDIT_BENCH, -1)
    aud = ad._make_step_config(  # pyright: ignore[reportPrivateUsage]
        v, "auditor", final, "sha", provenance="p", audit_max_additions=6
    )
    aud_name = ad._config_name(  # pyright: ignore[reportPrivateUsage]
        aud,
        ad._NO_UID,  # pyright: ignore[reportPrivateUsage]
    )
    assert aud_name == "step40_auditor_final"
    assert aud.audit_max_additions == 6 and aud.reducer_contract == 2


def test_role_runner_evicts_stale_same_name_cells() -> None:
    """A config re-registered under an existing name with different
    params must not reuse the old directory (HINTS #65)."""
    import yaml

    import ace_adaptation as ad
    from delphyne.utils.typing import pydantic_dump

    def cfg(upstream: str) -> ad.ACEAdaptStepConfig:
        return ad.ACEAdaptStepConfig(
            role="reducer",
            step=0,
            bench_name="t",
            seed=0,
            model_name="m",
            toolset="core",
            reasoning_effort="medium",
            num_requests=3,
            max_dollar_budget=0.02,
            playbook_sha256="pb",
            upstream_sha256=upstream,
        )

    with tempfile.TemporaryDirectory(dir=ad._OMPHALOS_DIR) as tmp:  # pyright: ignore[reportPrivateUsage]
        rel = str(Path(tmp).relative_to(ad._OMPHALOS_DIR))  # pyright: ignore[reportPrivateUsage]
        runner = ad.RoleRunner(ad.ACEAdaptStepConfig, rel, ad._config_name)  # pyright: ignore[reportPrivateUsage]
        old = cfg("old")
        name = ad._config_name(old, ad._NO_UID)  # pyright: ignore[reportPrivateUsage]
        state = {
            "name": "x",
            "description": None,
            "configs": {
                name: {
                    "params": pydantic_dump(ad.ACEAdaptStepConfig, old),
                    "status": "done",
                }
            },
        }
        (Path(tmp) / "experiment.yaml").write_text(yaml.safe_dump(state))
        cell = Path(tmp) / "configs" / name
        cell.mkdir(parents=True)
        (cell / "result.yaml").write_text("stale: true\n")
        # Same params: nothing happens.
        assert runner._evict_stale([cfg("old")]) == []  # pyright: ignore[reportPrivateUsage]
        assert cell.exists()
        # Different upstream hash, same name: the stale cell goes.
        assert runner._evict_stale([cfg("new")]) == [name]  # pyright: ignore[reportPrivateUsage]
        assert not cell.exists()


def test_reflector_scope_is_not_in_default_identity() -> None:
    from delphyne.utils.typing import pydantic_dump

    import ace_adaptation as ad

    cfg = ad.ACEAdaptStepConfig(
        role="reflector",
        step=0,
        bench_name="t",
        seed=0,
        model_name="m",
        toolset="core",
        reasoning_effort="medium",
        num_requests=3,
        max_dollar_budget=0.02,
        playbook_sha256="x",
    )
    dumped = cast(
        dict[str, Any],
        pydantic_dump(ad.ACEAdaptStepConfig, cfg, exclude_defaults=True),
    )
    assert "reflector_scope" not in dumped, dumped


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
