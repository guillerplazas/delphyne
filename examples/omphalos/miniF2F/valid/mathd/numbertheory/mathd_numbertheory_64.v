(* miniF2F problem: mathd_numbertheory_64
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the smallest positive integer that satisfies the congruence $30x \equiv 42
   \pmod{47}$? Show that it is 39.

   Informal proof:
   Note that 6 divides both $30x$ and $42$, and since 6 is relatively prime to 47, we
   can write $5x \equiv 7 \pmod{47}$. Note that $5 \cdot 19 = 95 = 2(47) + 1$, so 19 is
   the modular inverse of 5, modulo 47. We multiply both sides of the given congruence
   by 19 to obtain $95x \equiv 19(7) \pmod{47}\implies x \equiv 39 \pmod{47}$.
*)

Require Import Coq.Init.Nat.



Theorem mathd_numbertheory_64 :
  (30 * 39) mod 47 = 42 /\
  (forall x, (30 * x) mod 47 = 42 -> 39 <= x).

Proof.
Admitted.
