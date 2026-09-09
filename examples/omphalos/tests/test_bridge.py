"""
Installation smoke test for the pytanque <-> Rocq bridge.

Run `python test_bridge.py` (from any cwd) after setting up the
environment: it opens a session on `test_bridge.v`, replays one tactic,
and reports the proof state. Independent of the Delphyne baselines.
"""

from pathlib import Path

from pytanque import Pytanque, PytanqueMode

_TEST_FILE = str(Path(__file__).resolve().parent / "test_bridge.v")


def main():
    print("Starting Pytanque client in STDIO mode...")

    with Pytanque(mode=PytanqueMode.STDIO) as client:
        print("Connected to Rocq (via pet)!")

        state = client.start(_TEST_FILE, "my_test")
        print(f"Initial state ID: {state.st}")
        print(f"Is proof finished? {state.proof_finished}")

        goals = client.goals(state)
        print(f"\nInitial Goals (Count: {len(goals)}):")
        print(goals)

        print("\nExecuting tactic: 'reflexivity.'")
        state = client.run(state, "reflexivity.", verbose=True)

        new_goals = client.goals(state)
        print(f"\nGoals after tactic (Count: {len(new_goals)}):")
        print(new_goals)
        print(f"Is proof finished? {state.proof_finished}")


if __name__ == "__main__":
    main()
