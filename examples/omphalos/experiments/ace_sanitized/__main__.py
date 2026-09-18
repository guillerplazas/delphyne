"""Both harnesses: python -m experiments.ace_sanitized ACTION."""

import sys

from . import campaign as c


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "run-batch":
        batch = sys.argv[2]
        sys.argv = [sys.argv[0], *sys.argv[3:]]
        c.run_batch(batch)
    elif action in ("prepare", "seal", "verify", "pilot"):
        getattr(c, action)()
    elif action in ("prepare-roles", "role-pilots", "assess-roles", "adapt"):
        from . import learning

        getattr(
            learning,
            {
                "prepare-roles": "prepare_pilots",
                "role-pilots": "pilots",
                "assess-roles": "assess_pilots",
                "adapt": "adapt",
            }[action],
        )()
    elif action in ("combination", "freeze", "benchmark"):
        from . import workflow

        getattr(workflow, action)()
    else:
        raise SystemExit(
            "prepare | prepare-roles | seal | role-pilots | assess-roles | "
            "adapt | pilot | combination | freeze | benchmark | verify | "
            "run-batch NAME ..."
        )


if __name__ == "__main__":
    main()
