"""
Baseline: see and repair the whole proof.
"""

from dataclasses import dataclass

import delphyne as dp

import checker as ch


@dataclass
class ProveEqualityAtOnce(dp.Query[ch.Proof]):
    equality: ch.Eq

    def parse(self, answer: dp.Answer) -> ch.Proof:
        """
        Parse and check the proof at once.
        """

        assert isinstance(answer.content, str)
        proof: ch.Proof = dp.yaml_from_last_block(ch.Proof, answer.content)
        ret = ch.check(self.equality, proof, ch.TRIG_RULES)
        if isinstance(ret, ch.ProofError):
            raise dp.ParseError(description=str(ret))
        return proof

    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}


def ask_gpt_iteratively(model: str) -> dp.PromptingPolicy:
    llm = dp.openai_model(model)
    return dp.few_shot(llm, iterative_mode=True)