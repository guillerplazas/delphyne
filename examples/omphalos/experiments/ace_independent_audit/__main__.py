"""Both CLIs: python -m experiments.ace_independent_audit ACTION."""

import sys

from . import campaign


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    from .common import CAMPAIGN

    if (CAMPAIGN / "HOLD_NEW_BATCHES.json").exists() and action in (
        "run-batch",
        "run-roles",
        "run-teacher",
        "run-online-teacher",
    ):
        raise SystemExit(
            "User-requested dispatch hold: existing batches may finish; "
            "no new solver, author or teacher batch is started. "
            "See HOLD_NEW_BATCHES.json."
        )
    if action == "prepare":
        campaign.prepare()
    elif action == "run-batch":
        batch = sys.argv[2]
        sys.argv = [sys.argv[0], *sys.argv[3:]]
        campaign.run_batch(batch)
    elif action == "audit":
        from .audit import run

        run()
    elif action == "run-roles":
        from .workflow import run_roles

        batch = sys.argv[2]
        sys.argv = [sys.argv[0], *sys.argv[3:]]
        run_roles(batch)
    elif action in (
        "prepare-evidence",
        "ladder",
        "prepare-author-pilot",
        "assess-author-pilot",
    ):
        from . import workflow

        getattr(workflow, action.replace("-", "_"))()
    elif action in ("prepare-teacher", "run-teacher", "collect-teacher"):
        from . import teacher

        getattr(teacher, action.split("-")[0])()
    elif action in ("prepare-full-learning", "full-learning"):
        from . import final_learning

        if action == "prepare-full-learning":
            final_learning.prepare()
        else:
            final_learning.run(sys.argv[2])
    elif action in (
        "prepare-core",
        "prepare-online",
        "prepare-scaling",
        "online",
        "run-online-teacher",
    ):
        from . import core

        if action == "prepare-core":
            core.prepare()
        elif action == "prepare-online":
            core.prepare_online()
        elif action == "prepare-scaling":
            core.prepare_scaling()
        elif action == "online":
            core.online(int(sys.argv[2]))
        else:
            batch = sys.argv[2]
            sys.argv = [sys.argv[0], *sys.argv[3:]]
            core.run_teacher_batch(batch)
    else:
        raise SystemExit(
            "prepare | audit | run-batch NAME run --max_workers=16 --wait"
        )


if __name__ == "__main__":
    main()
