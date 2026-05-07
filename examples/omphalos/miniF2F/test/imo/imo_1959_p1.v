(* miniF2F problem: imo_1959_p1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Prove that the fraction $\frac{21n+4}{14n+3}$ is irreducible for every natural number
   $n$.

   Informal proof:
   Denoting the greatest common divisor of $a, b $ as $(a,b) $, we use the [[Euclidean
   algorithm]]:

   $(21n+4, 14n+3) = (7n+1, 14n+3) = (7n+1, 1) = 1$

   It follows that $\frac{21n+4}{14n+3}$ is irreducible.  Q.E.D.
*)

Require Import Nat.
Require Import Arith.

Theorem imo_1959_p1 :
  forall n : nat, gcd (21 * n + 4) (14 * n + 3) = 1.
Proof.
Admitted.