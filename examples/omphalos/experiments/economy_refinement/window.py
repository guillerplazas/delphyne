"""Bounded history drops; no summary, retrieval memory or additional tool."""

from collections.abc import Callable
from dataclasses import dataclass, replace

import delphyne as dp

from ace.ace_grounded import Checked
from prove_economy import interaction_groups, visible_chars
from prove_grounded import ProposeProofScriptGrounded
from runtime.admission_events import record


@dataclass
class RefinedWindow:
    min_groups: int = 8
    threshold_chars: int = 24000
    minimum_removed_chars: int = 8192
    max_resets: int = 2
    cut: int = 0
    retained: tuple[int, ...] = ()
    resets: int = 0
    previous_groups: int = 0

    def apply(
        self,
        query: ProposeProofScriptGrounded,
        render: Callable[
            [ProposeProofScriptGrounded], ProposeProofScriptGrounded
        ],
    ) -> tuple[ProposeProofScriptGrounded, bool]:
        groups = interaction_groups(query.prefix)
        if len(groups) < self.previous_groups:
            raise ValueError("Session control requires append-only history")
        self.previous_groups = len(groups)
        active = [
            i
            for i in range(len(groups))
            if i >= self.cut or i in self.retained
        ]

        def projected(indices: list[int]) -> ProposeProofScriptGrounded:
            return render(
                replace(
                    query, prefix=tuple(m for i in indices for m in groups[i])
                )
            )

        current = projected(active)
        before = visible_chars(current.prefix)
        if (
            self.resets >= self.max_resets
            or len(groups) - self.cut < self.min_groups
            or before < self.threshold_chars
        ):
            return current, False
        required = set(active[-2:])
        checked = next(
            (
                i
                for i in reversed(active)
                if any(
                    isinstance(m, dp.FeedbackMessage)
                    and isinstance(m.meta, Checked)
                    for m in groups[i]
                )
            ),
            None,
        )
        if checked is not None:
            required.add(checked)
        candidate = projected(sorted(required))
        after = visible_chars(candidate.prefix)
        if before - after < self.minimum_removed_chars:
            return current, False
        self.cut = len(groups)
        self.retained = tuple(sorted(required))
        self.resets += 1
        record(
            "refined_session",
            "reset",
            reset=self.resets,
            groups=len(groups),
            retained=self.retained,
            before_chars=before,
            after_chars=after,
            verified_prefix_chars=len(query.verified_prefix),
        )
        return candidate, True
