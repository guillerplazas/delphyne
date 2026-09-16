"""Live Rocq with mocked HTTP: a session handoff must replay exactly."""

from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib import openai_api as oa
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.models import LLMOutput, LLMRequest, LLMResponse
from delphyne.stdlib.tasks import run_command
import pytest

from experiments import ace_economy_experiment as c
from runtime.campaign_budget import CampaignResponsesModel, Ledger


def test_session_handoff_preserves_transport_and_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(1, {"test": 1})
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_LEDGER", str(ledger.path))
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "test")
    monkeypatch.setenv("OMPHALOS_ESTIMATE_DOLLARS", "1")
    monkeypatch.setenv(
        "OMPHALOS_ADMISSION_EVENTS", str(tmp_path / "events.jsonl")
    )
    file = c.partition("validation")["aime_1984_p7"]
    args = dp.RunStrategyArgs(
        strategy="prove_theorem_grounded",
        args=dict(
            problem_file=file,
            theorem_name="aime_1984_p7",
            turn_budget=12,
            admission=False,
            restart=False,
        ),
        policy="economy_proof_policy",
        budget=dict(price=0.10, num_requests=12, rocq_seconds=300),
        policy_args=dict(
            snapshot_directory=str(tmp_path / "transport"),
            pause_file=str(tmp_path / "PAUSED"),
            split_session=True,
        ),
        cache_file=str(tmp_path / "cache.yaml"),
        export_raw_trace=False,
        export_browsable_trace=False,
        export_log=False,
    )
    calls: list[dict[str, Any]] = []

    def fake_send(
        self: CampaignResponsesModel, req: LLMRequest
    ) -> LLMResponse:
        translated, _ = oa.translate_chat_for_responses(
            req, self.reasoning_cache, self.convert_user_feedback_to_tool
        )
        calls.append(dict(length=len(str(translated)), input=translated))
        # Exercise a nonempty transport state, including when the shortened
        # conversation repeats a prompt seen in the first session.
        self.reasoning_allowance += 1
        if len(calls) % 2:
            output = LLMOutput(
                "Reasoning placeholder. " * 400
                + "\n```rocq\nthis_tactic_does_not_exist.\n```"
            )
        else:
            output = LLMOutput(
                "",
                (
                    dp.ToolCall(
                        "SearchRocq", dict(command="Check Nat.add_comm.")
                    ),
                ),
            )
        return LLMResponse(
            [output],
            dp.Budget(
                dict(
                    price=0.0001,
                    num_requests=1,
                    input_tokens=1,
                    output_tokens=1,
                )
            ),
            model_name="gpt-5.6-luna",
        )

    with (
        patch.object(CampaignResponsesModel, "_send_final_request", fake_send),
        redirect_stdout(io.StringIO()),
    ):
        result = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    assert result.result is not None
    assert len(calls) == 12
    assert calls[8]["length"] < calls[7]["length"]
    events = [
        json.loads(s)
        for s in (tmp_path / "events.jsonl").read_text().splitlines()
    ]
    resets = [e for e in events if e["kind"] == "economy_session"]
    assert (
        len(resets) == 1
        and resets[0]["before_chars"] > resets[0]["after_chars"]
    )
    args.cache_mode = "replay"
    with (
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Replay must not call HTTP"),
        ),
        redirect_stdout(io.StringIO()),
    ):
        repeated = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    assert repeated.result is not None
    assert repeated.result.success == result.result.success
    assert repeated.result.spent_budget == result.result.spent_budget
    assert repeated.result.values == result.result.values
    assert ledger.summary()["liability"] == 0
