"""Both harnesses: python -m experiments.ace_x3_reproduction ACTION."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=("audit", "retrieve", "prepare", "run", "verify", "report"),
    )
    action = parser.parse_args().action
    if action in ("prepare", "run"):
        from . import campaign

        getattr(campaign, action)()
    elif action in ("audit", "retrieve"):
        from . import audit

        getattr(audit, action)()
    elif action == "verify":
        from .verification import verify

        verify()
    else:
        from .report import report

        report()


if __name__ == "__main__":
    main()
