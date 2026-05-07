(* miniF2F problem: imo_1964_p1_2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any natural number $n$, $7$ does not divide $2^n + 1$.

   Informal proof:
   If $2^n+1$ is congruent to 0 mod 7, then $2^n$ must be congruent to 6 mod 7, but this
   is not possible due to how $2^n$ mod 7 cycles. Therefore, there is no solution.
*)

Require Import Nat.
Require Import ZArith.

Theorem imo_1964_p1_2:
  forall n : nat, ~(Nat.divide 7 (2^n + 1)).
Proof.
Admitted.