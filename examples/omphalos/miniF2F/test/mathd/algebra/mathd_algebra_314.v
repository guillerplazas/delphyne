(* miniF2F problem: mathd_algebra_314
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $n = 11$, then what is $\left(\frac{1}{4}\right)^{n+1} \cdot 2^{2n}$? Show that it
   is \frac{1}{4}.

   Informal proof:
   By simplifying exponents, we have $2^{2n} = 4^n$.  So, our overall expression is
   $\frac{4^n}{4^{n+1}}$.  This simplifies to $\frac{1}{4}$.  Throughout the course of
   this calculation, we did not have to plug in the value of 11 for $n$, but the answer
   may be similarly obtained with this substitution.
*)

Require Import Reals.

Open Scope R_scope.

Theorem mathd_algebra_314
  (n : nat)
  (h₀ : n = 11%nat) :
  (1 / 4) ^ (n + 1) * 2 ^ (2 * n) = 1 / 4.

Proof.
Admitted.
