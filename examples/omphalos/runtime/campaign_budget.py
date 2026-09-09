"""Opt-in, process-safe admission and receipts for paid ACE campaigns.

The ordinary Delphyne dollar budget is a stopping rule, not a billing
ceiling. This ledger reserves a request's upper bound before dispatch.
Unknown charges retain their entire reservation; crashed workers never
silently release money. Cached requests bypass the adapter and cost zero.
Both agent harnesses use the same Python adapter and SQLite ledger.
"""

# pyright: strict

import json
import math
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any, override

import openai
from openai import omit

from delphyne.stdlib import openai_api as oa
from delphyne import Budget
from delphyne.stdlib.models import (
    LLM,
    LLMBusyException,
    LLMRequest,
    LLMResponse,
)


class CampaignExhausted(RuntimeError):
    """No more requests can be admitted within a campaign allocation."""


class Ledger:
    def __init__(self, path: Path):
        self.path = path

    def create(self, ceiling: float, stages: dict[str, float]) -> None:
        if (
            not math.isfinite(ceiling)
            or ceiling <= 0
            or any(not math.isfinite(v) or v <= 0 for v in stages.values())
        ):
            raise ValueError("budgets must be positive")
        if sum(stages.values()) > ceiling + 1e-9:
            raise ValueError("stage allocations exceed campaign ceiling")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS settings (config TEXT)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS allocation_origin (config TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS transfers (created REAL, source TEXT, target TEXT, amount REAL, reason TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS receipts ("
                "id TEXT PRIMARY KEY, stage TEXT, model TEXT, pid INTEGER, "
                "created REAL, reserved REAL, charged REAL, status TEXT, "
                "usage TEXT, cell TEXT)"
            )
            if "cell" not in {
                r[1] for r in db.execute("PRAGMA table_info(receipts)")
            }:
                db.execute("ALTER TABLE receipts ADD COLUMN cell TEXT")
            config = json.dumps([ceiling, stages], sort_keys=True)
            old = db.execute("SELECT config FROM settings").fetchone()
            origin = db.execute(
                "SELECT config FROM allocation_origin"
            ).fetchone()
            original_config = (
                origin[0]
                if origin is not None
                else old[0]
                if old is not None
                else config
            )
            if original_config != config:
                raise ValueError("ledger already has a different allocation")
            if origin is None:
                db.execute(
                    "INSERT INTO allocation_origin VALUES (?)",
                    (original_config,),
                )
            if old is None:
                db.execute("INSERT INTO settings VALUES (?)", (config,))

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=60)

    def transfer(
        self, source: str, target: str, amount: float, reason: str
    ) -> None:
        """Move unused stage capacity; total authorization never changes."""
        if (
            not math.isfinite(amount)
            or amount <= 0
            or not reason.strip()
            or source == target
        ):
            raise ValueError("invalid allocation transfer")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            ceiling, stages = json.loads(
                db.execute("SELECT config FROM settings").fetchone()[0]
            )
            if source not in stages or target not in stages:
                raise ValueError("unknown allocation")
            used = float(
                db.execute(
                    "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM receipts WHERE stage=?",
                    (source,),
                ).fetchone()[0]
            )
            if stages[source] - amount < used - 1e-9:
                raise CampaignExhausted(
                    "cannot transfer committed or reserved money"
                )
            stages[source] -= amount
            stages[target] += amount
            db.execute(
                "UPDATE settings SET config=?",
                (json.dumps([ceiling, stages], sort_keys=True),),
            )
            db.execute(
                "INSERT INTO transfers VALUES (?,?,?,?,?)",
                (time.time(), source, target, amount, reason),
            )

    def reserve(
        self, stage: str, model: str, amount: float, cell: str = ""
    ) -> str:
        if not math.isfinite(amount) or amount <= 0:
            raise ValueError("reservation must be positive")
        deadline = time.monotonic() + 1800
        while True:
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT config FROM settings").fetchone()
                if row is None:
                    raise ValueError("uninitialized campaign ledger")
                ceiling, stages = json.loads(row[0])
                if stage not in stages:
                    raise ValueError(f"unknown campaign stage: {stage}")
                totals = db.execute(
                    "SELECT stage, SUM(COALESCE(charged,reserved)), "
                    "SUM(CASE WHEN charged IS NULL THEN reserved ELSE 0 END) "
                    "FROM receipts GROUP BY stage"
                ).fetchall()
                used = sum(float(r[1]) for r in totals)
                pending = sum(float(r[2]) for r in totals)
                own = next((float(r[1]) for r in totals if r[0] == stage), 0)
                own_pending = next(
                    (float(r[2]) for r in totals if r[0] == stage), 0
                )
                if used + amount <= ceiling and own + amount <= stages[stage]:
                    key = uuid.uuid4().hex
                    db.execute(
                        "INSERT INTO receipts VALUES (?,?,?,?,?,?,NULL,?,NULL,?)",
                        (
                            key,
                            stage,
                            model,
                            os.getpid(),
                            time.time(),
                            amount,
                            "in_flight",
                            cell,
                        ),
                    )
                    return key
                if (
                    used - pending + amount > ceiling
                    or own - own_pending + amount > stages[stage]
                    or time.monotonic() >= deadline
                ):
                    raise CampaignExhausted(
                        f"{stage}: committed ${own - own_pending:.4f}; "
                        f"cannot reserve ${amount:.4f}"
                    )
            time.sleep(0.25)

    def settle(
        self, key: str, charge: float | None, usage: dict[str, Any]
    ) -> None:
        if charge is not None and (not math.isfinite(charge) or charge < 0):
            raise ValueError("invalid charge; reservation remains in force")
        exceeded = False
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT reserved,charged FROM receipts WHERE id=?", (key,)
            ).fetchone()
            if row is None or row[1] is not None:
                raise ValueError("missing or already settled reservation")
            # Unknown billing is a liability, never a free retry.
            actual = float(row[0]) if charge is None else charge
            status = "unknown_charge" if charge is None else "settled"
            db.execute(
                "UPDATE receipts SET charged=?,status=?,usage=? WHERE id=?",
                (actual, status, json.dumps(usage, sort_keys=True), key),
            )
            exceeded = actual > float(row[0]) + 1e-9
        if exceeded:
            # Preserve the actual charge even when the bound was violated.
            raise RuntimeError("billing exceeded the reserved upper bound")

    def summary(self) -> dict[str, Any]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT stage,status,COUNT(*),SUM(COALESCE(charged,reserved)) "
                "FROM receipts GROUP BY stage,status"
            ).fetchall()
            ceiling, allocations = json.loads(
                db.execute("SELECT config FROM settings").fetchone()[0]
            )
            transfers = db.execute("SELECT * FROM transfers").fetchall()
        return {
            "ceiling": ceiling,
            "allocations": allocations,
            "transfers": [
                dict(
                    zip(("created", "source", "target", "amount", "reason"), r)
                )
                for r in transfers
            ],
            "liability": sum(float(r[3]) for r in rows),
            "groups": [
                dict(zip(("stage", "status", "requests", "dollars"), r))
                for r in rows
            ],
        }


@dataclass(kw_only=True)
class CampaignResponsesModel(oa.OpenAIResponsesModel):
    """Responses transport with one visible, reserved HTTP attempt.

    Uses Delphyne's request translation and response parsing unchanged. SDK
    retries are disabled: every retry by the policy gets its own receipt.
    Input admission bounds UTF-8 payload bytes (at most one text token per
    byte), all prior generated tokens for opaque reasoning references, and
    32K tokens of framing allowance. Images/audio are not used by this
    campaign. Actual usage is checked against the reservation on every call.
    """

    ledger_file: str
    stage: str
    cell: str = ""
    reasoning_allowance: int = field(init=False, default=0)
    output_limit: int = 32768
    estimate_dollars: bool = False

    def _input_bound(self, req: LLMRequest) -> int:
        inp, _ = oa.translate_chat_for_responses(
            req, self.reasoning_cache, self.convert_user_feedback_to_tool
        )
        tools = [oa._make_responses_tool(t) for t in req.tools]  # pyright: ignore[reportPrivateUsage]
        fmt = oa._responses_response_format(  # pyright: ignore[reportPrivateUsage]
            req.structured_output, self.no_json_schema
        )
        return (
            len(json.dumps([inp, tools, fmt], default=str).encode())
            + self.reasoning_allowance
            + 32768
        )

    @override
    def estimate_budget(self, req: LLMRequest) -> Budget:
        estimate = super().estimate_budget(req)
        if not self.estimate_dollars:
            return estimate
        full = self.add_model_defaults(req)
        assert self.pricing is not None
        bound = (
            self._input_bound(full) * self.pricing.dollars_per_input_token
            + full.options.get("max_completion_tokens", self.output_limit)
            * self.pricing.dollars_per_output_token
        )
        return estimate + Budget({"price": bound})

    @override
    def add_model_defaults(self, req: LLMRequest) -> LLMRequest:
        req = super().add_model_defaults(req)
        return replace(
            req,
            options={
                **req.options,
                "max_completion_tokens": min(
                    req.options.get(
                        "max_completion_tokens", self.output_limit
                    ),
                    self.output_limit,
                ),
            },
        )

    @override
    def _send_final_request(self, req: LLMRequest) -> LLMResponse:
        if req.num_completions != 1:
            raise ValueError("campaign transport requires one completion")
        assert self.pricing is not None
        options = req.options
        assert "model" in options and "max_completion_tokens" in options
        inp, log = oa.translate_chat_for_responses(
            req, self.reasoning_cache, self.convert_user_feedback_to_tool
        )
        tools = [oa._make_responses_tool(t) for t in req.tools]  # pyright: ignore[reportPrivateUsage]
        fmt = oa._responses_response_format(  # pyright: ignore[reportPrivateUsage]
            req.structured_output, self.no_json_schema
        )
        bound_input = self._input_bound(req)
        bound = (
            bound_input * self.pricing.dollars_per_input_token
            + options["max_completion_tokens"]
            * self.pricing.dollars_per_output_token
        )
        ledger = Ledger(Path(self.ledger_file))
        key = ledger.reserve(self.stage, options["model"], bound, self.cell)
        try:
            with openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                max_retries=0,
                timeout=600,
            ) as client:
                response = client.responses.create(
                    model=options["model"],
                    input=inp,
                    temperature=options.get("temperature", omit),
                    reasoning={"effort": options["reasoning_effort"]}
                    if "reasoning_effort" in options
                    else omit,
                    max_output_tokens=options["max_completion_tokens"],
                    top_logprobs=options.get("top_logprobs", omit),
                    tools=tools if tools else omit,
                    text=fmt,
                    tool_choice=options.get("tool_choice", omit),
                    include=["message.output_text.logprobs"]
                    if options.get("logprobs", False)
                    else [],
                    store=True,
                )
        except Exception as ex:
            rejected = isinstance(ex, openai.APIStatusError) and (
                ex.status_code in {400, 401, 403, 404, 422, 429}
            )
            ledger.settle(
                key,
                0.0 if rejected else None,
                {"exception": type(ex).__name__},
            )
            if isinstance(ex, (openai.RateLimitError, openai.APITimeoutError)):
                raise LLMBusyException(ex) from ex
            raise
        usage = response.usage
        if usage is None:
            ledger.settle(key, None, {"response_id": response.id})
            raise RuntimeError("response has no billing usage")
        spent = oa._compute_spent_budget(  # pyright: ignore[reportPrivateUsage]
            1, self.model_class, self.pricing, usage
        )
        ledger.settle(
            key,
            spent["price"],
            {
                **usage.to_dict(),
                "response_id": response.id,
                "model": response.model,
                "input_bound": bound_input,
                "status": response.status,
                "http_timeout_seconds": 600,
            },
        )
        self.reasoning_allowance += usage.output_tokens
        output, parsed_log = self._parse_response(response, req)
        return LLMResponse(
            [] if output is None else [output],
            Budget(spent),
            [*log, *parsed_log],
            response.model,
            usage.to_dict(),
        )


def for_campaign(model: LLM) -> LLM:
    """Wrap only explicitly opted-in Responses campaigns."""
    path = os.environ.get("OMPHALOS_CAMPAIGN_LEDGER")
    if not path:
        return model
    if not isinstance(model, oa.OpenAIResponsesModel):
        raise ValueError("campaign ledger supports Responses models only")
    args: dict[str, Any] = {
        f.name: getattr(model, f.name) for f in fields(model) if f.init
    }
    return CampaignResponsesModel(
        **args,
        ledger_file=str(Path(path).resolve()),
        stage=os.environ["OMPHALOS_CAMPAIGN_STAGE"],
        cell=os.environ.get("OMPHALOS_CAMPAIGN_CELL", ""),
        estimate_dollars=os.environ.get("OMPHALOS_ESTIMATE_DOLLARS") == "1",
    )
