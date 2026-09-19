"""Both harnesses: python -m experiments.ace_thesis ACTION."""

import sys

from . import campaign as c


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "run-batch":
        batch = sys.argv[2]
        sys.argv = [sys.argv[0], *sys.argv[3:]]
        c.run_batch(batch)
    elif action in ("prepare", "seal", "verify"):
        getattr(c, action)()
    elif action in (
        "prepare-artifacts",
        "round1",
        "round2",
        "freeze",
        "benchmark",
    ):
        from . import workflow

        getattr(workflow, action.replace("-", "_"))()
    elif action == "adapt":
        from .learning import adapt

        adapt()
    elif action in ("replay", "kernel"):
        from . import verify_results

        if action == "kernel":
            verify_results.kernel()
        else:
            for path in sorted((c.CAMPAIGN / "batches").glob("*.json")):
                verify_results.replay(path.stem)
    else:
        raise SystemExit(
            "prepare | prepare-artifacts | seal | verify | round1 | adapt | round2 | freeze | benchmark | replay | kernel | run-batch NAME ..."
        )


if __name__ == "__main__":
    main()
