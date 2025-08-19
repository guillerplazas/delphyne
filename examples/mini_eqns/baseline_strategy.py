
"""
Baseline: conversational agent that produces a proof in one go and is
then provided opportunities to fix errors from the checker.

This example illustrate how simple conversational agents can be built
with a single query, using the `iterative_mode` option of `few_shot`.
"""

from dataclasses import dataclass
from typing import override, Never #,ClassVar
import delphyne as dp
from delphyne import Branch, Computation, Strategy, dfs, strategy
import checker as ch  # assuming checker is available as ch

@dataclass
class ProveEqualityAtOnce(dp.Query[ch.Proof]):
    equality: ch.Eq
    #prefix: str = ""

    @override
    def parser(self) -> dp.Parser[ch.Proof]:
        # Note: an explicit type annotation is needed here, until Python
        # 3.14 introduces `TypeExpr`. See `yaml_as` docstring.
        parser: dp.Parser[ch.Proof] = dp.last_code_block.yaml_as(ch.Proof)
        return parser.validate(
            lambda proof: dp.ParseError(description=str(ret))
            if isinstance(
                ret := ch.check(self.equality, proof, ch.TRIG_RULES),
                ch.ProofError,
            )
            else None
        )
        #assert isinstance(answer.content, str) 

    @override
    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}
    
    """
    def parse(self, answer: dp.Answer) -> dp.Response[ch.Proof, Never]:
        assert isinstance(answer.content, str)
        #proof: ch.Proof = dp.yaml_from_last_block(ch.Proof, answer.content)
        try:
            proof: ch.Proof = dp.yaml_from_last_block(ch.Proof, answer.content)
        except dp.ParseError as e:
            raise dp.ParseError(description=f"Failed to parse proof from answer: {e}")
    
        return dp.Response(answer=answer, parsed=dp.FinalAnswer(proof))
    # Final answer is a ch.Proof object, which is the result of the LLM's proof attempt.- distinguis it from a tool call
    """



@strategy
def check_equality(equality: ch.Eq, proof: ch.Proof) -> Strategy[Computation, object, ch.Proof | dp.Error]:
    """Compute strategy to check a proposed proof. Returns the proof if correct, or feedback as Error if incorrect."""
    # Run the checker on the target equality and the proposed proof.
    feedback = yield from dp.compute(ch.check, equality, proof, ch.TRIG_RULES)
    # Assume feedback has an attribute 'valid' (boolean) or similar to indicate success.
    """if getattr(feedback, "success", False) or getattr(feedback, "valid", False):
        # Proof is correct; return it as the final result.
        return proof
    """
    if feedback is None:
        # Proof is correct; return it as the final result.
        return proof
    # Proof is incorrect – prepare feedback for the LLM.
    # Optionally, refine the feedback object to only include what's necessary.
    # (For example, remove any parts of proof that were correct, or format a message.)
    # Here, we assume `feedback` itself is either a message or an object with details.
    #return dp.Error(label="feedback", meta={"error": str(feedback)})
    return dp.Error(label="feedback", meta=feedback)
    #return dp.Error(label="repair", meta=feedback)
    #raise dp.ParseError(description=str(feedback))


@strategy
def prove_equality_interactive(equality: ch.Eq
                               ) -> Strategy[Branch, dp.PromptingPolicy, ch.Proof]:
    """
    Interactive strategy to prove a trigonometric equality.
    Queries the LLM iteratively, using checker feedback to refine the proof.
    Returns a ch.Proof on success, or propagates an Error if unsuccessful.
    """
    # Use dp.interact to manage the LLM interaction with feedback loop
    result_proof = yield from dp.interact(
        step=lambda prefix, _: 
            #ProveEqualityAtOnce(equality, prefix).using(dp.ambient_pp),
            ProveEqualityAtOnce(equality, prefix).using(dp.ambient_pp),

        process=lambda proof, _: 
            check_equality(equality, proof).using(dp.just_compute)
    )
    # If we exit the loop with a proof (i.e., not an Error), return it
    return result_proof

def prove_equality_interactive_policy(
    model_name: dp.StandardModelName, 
    temperature: float | None = None, 
    max_feedback_cycles: int = 3):
    """
    Returns a (search_policy, prompting_policy) pair for the interactive equality-proving strategy.
    - model_name: which LLM to use (e.g., dp.StandardModelName.GPT4 or a string for the model).
    - temperature: sampling temperature for the LLM (if applicable).
    - max_feedback_cycles: how many rounds of feedback to allow at most.
    """
    model = dp.standard_model(model_name)
    # Search policy: allow looping with a DFS bound on depth to limit feedback cycles
    sp = dp.loop() @ dfs(max_depth=2 * (max_feedback_cycles + 1))
    # Prompting policy: few-shot prompting with the chosen model and parameters
    #pp = dp.few_shot(model, temperature=temperature, max_requests=1)
    pp = dp.few_shot(model, enable_logging=False, temperature=temperature, max_requests=1,iterative_mode=False)
    return (sp, pp)


