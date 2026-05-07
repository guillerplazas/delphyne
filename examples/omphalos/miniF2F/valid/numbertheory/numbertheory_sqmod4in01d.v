(* miniF2F problem: numbertheory_sqmod4in01d
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For any integer $a$, show that $a^2 \equiv 0 \pmod{4}$ or $a^2 \equiv 1 \pmod{4}$.

   Informal proof:
   $a \pmod 4 \in {0, 1, 2, 3}$.
   Using that for any natural number $k$, $a \equiv b \pmod 4$ implies $a^k \equiv b^k
   \pmod 4$, we have  $a^2 \pmod 4 \in {0, 1, 4, 9}$. Since $4 \equiv 0 \pmod 4$ and $9
   \equiv 1 \pmod 4$, the result follows.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem numbertheory_sqmod4in01d :
  forall a : Z, (a^2 mod 4 = 0) \/ (a^2 mod 4 = 1).
Proof.
Admitted.