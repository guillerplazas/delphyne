(* miniF2F problem: induction_nfactltnexpnm1ngt3
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any integer $n \geq 3$, we have $n! < n^{n-1}$.

   Informal proof:
   The term $n (n-1) \dots (n-(n-3))$ is composed of $n-2$ terms smaller or equal to
   $n$, so $n (n-1) \dots (n-(n-3)) \leq n^{n-2}$. Since $n \geq 3 > 2 \times 1$, we
   have:
   $$n! = \left( n (n-1) \dots (n-(n-3)) \right) \times (2 \cdot 1) > n^{n-2} \times n =
   n^{n-1}$$
*)

Require Import Arith.

Theorem induction_nfactltnexpnm1ngt3:
  forall (n : nat),
    3 <= n ->
    fact n < n^(n - 1).
Proof.
Admitted.