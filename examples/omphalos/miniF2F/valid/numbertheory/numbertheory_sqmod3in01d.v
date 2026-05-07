(* miniF2F problem: numbertheory_sqmod3in01d
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that the square of any integer is congruent to 0 or 1 modulo 3.

   Informal proof:
   Let $a$ be an integer, then $a \pmod 3 \in {0, 1, 2}$.
   Using that for any natural number $k$, $a \equiv b \pmod 3$ implies $a^k \equiv b^k
   \pmod 3$, we have $a^2 \pmod 3 \in {0, 1, 4}$. Since $4 \equiv 1 \pmod 3$ the result
   follows.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem numbertheory_sqmod3in01d (a : Z) :
  (a^2 mod 3 = 0) \/ (a^2 mod 3 = 1).
Proof.
Admitted.