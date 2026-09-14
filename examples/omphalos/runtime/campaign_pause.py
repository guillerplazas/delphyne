"""Cooperative pause before dispatch, without interrupting active HTTP calls.

Create the campaign pause file first and let supervised workers drain. Do
not terminate the wrapper while its supervisor is cleaning up an attempt.
Already admitted operations drain, including ones waiting for ledger space;
the flag blocks subsequent operations before reservation. No automatic
resumption is provided. This is cooperative cancellation, not process killing.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from delphyne.stdlib.models import LLMRequest, LLMResponse

from prove_ace_roles import RoleResponsesModel
from prove_resource_completion import CompletionResponsesModel


class CampaignPaused(RuntimeError):
    pass


def request_pause(path: Path, reason: str) -> bool:
    """Set an idempotent admission stop without interrupting active requests."""
    if not reason.strip():
        raise ValueError("A pause reason is required")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x") as out:
            json.dump(
                dict(
                    reason=reason,
                    time=datetime.now(timezone.utc).isoformat(),
                    resume=False,
                ),
                out,
            )
            out.write("\n")
    except FileExistsError:
        return False
    return True


@dataclass(kw_only=True)
class PauseAwareRoleModel(RoleResponsesModel):
    pause_file: str

    def _send_final_request(self, req: LLMRequest) -> LLMResponse:
        if Path(self.pause_file).exists():
            raise CampaignPaused(
                "Campaign paused before reservation and dispatch"
            )
        return super()._send_final_request(req)


@dataclass(kw_only=True)
class PauseAwareProofModel(CompletionResponsesModel):
    """The same admission stop with the unchanged flagship proof parser."""

    pause_file: str

    def _send_final_request(self, req: LLMRequest) -> LLMResponse:
        if Path(self.pause_file).exists():
            raise CampaignPaused(
                "Campaign paused before reservation and dispatch"
            )
        return super()._send_final_request(req)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("flag", type=Path)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    created = request_pause(args.flag, args.reason)
    print(
        json.dumps(
            dict(
                paused=True,
                created=created,
                message="New role requests blocked; let the supervised attempt drain",
            )
        )
    )


if __name__ == "__main__":
    main()
