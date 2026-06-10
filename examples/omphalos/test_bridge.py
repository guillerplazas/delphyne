# pytanque ships no type stubs, so strict mode is unusable here.
# pyright: basic
from pytanque import Pytanque, PytanqueMode

def main():
    print("Starting Pytanque client in STDIO mode...")
    
    # Notice we removed the 'command' argument and the 'async' keywords
    with Pytanque(mode=PytanqueMode.STDIO) as client:
        print("Connected to Rocq (via pet)!")
        
        # 1. Start the proof session by pointing it to the file and the Lemma name
        state = client.start("examples/omphalos/test_bridge.v", "my_test")
        print(f"Initial state ID: {state.st}")
        print(f"Is proof finished? {state.proof_finished}")
        
        # 2. Check the initial goals
        goals = client.goals(state)
        print(f"\nInitial Goals (Count: {len(goals)}):")
        print(goals)
        
        # 3. Execute a tactic
        print("\nExecuting tactic: 'reflexivity.'")
        state = client.run(state, "reflexivity.", verbose=True)
        
        # 4. Check the state again
        new_goals = client.goals(state)
        print(f"\nGoals after tactic (Count: {len(new_goals)}):")
        print(new_goals)
        print(f"Is proof finished? {state.proof_finished}")

if __name__ == "__main__":
    main()