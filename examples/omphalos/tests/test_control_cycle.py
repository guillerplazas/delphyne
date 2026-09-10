"""Registration guards for the 120-cell bounded ACE control cycle."""

from experiments.ace.ace_control_cycle_experiment import ALLOCATIONS, configs


def main() -> None:
    rows = configs("tuning")
    assert len(rows) == 40
    assert sum(ALLOCATIONS.values()) == 4.0
    assert all(row.seed == 0 and not row.resource_recovery for row in rows)
    assert {row.arm_label for row in rows} == {"tuning"}
    print("control-cycle registration checks passed")


if __name__ == "__main__":
    main()
