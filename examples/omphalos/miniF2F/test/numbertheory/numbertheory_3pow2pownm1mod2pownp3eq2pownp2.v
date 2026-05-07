(* miniF2F problem: numbertheory_3pow2pownm1mod2pownp3eq2pownp2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integer $n$, the remainder of $3^{2^n} - 1 \equiv 2^{n+2} \mod
   2^{n+3}$.

   Informal proof:
   We can prove this by induction on n. For the base case, $n=1$, when the result
   obviously holds.
   For the inductive case, the hypothesis is $3^{2^n} - 1 \equiv 2^{n+2} \mod 2^{n+3}$,
   so we can obtain a natural number $p$ where $3^{2^n} - 1 = 2^{n+2} + p * 2^{n+3} =
   2^{n+2}(1+2p)$.
   Then we have $3^{2^{n+1}} = 3^{2^n*2} = (3^{2^n})^2 = (2^{n+2} * (1+2p) + 1)^2$.
   Hence $3^{2^{n+1}} \equiv (2^{n+2} * (1+2p))^2 + 2 * 2^{n+2} * (1+2p) + 1 \equiv
   2^{n+3}*(1+2p) + 1 \equiv 1\mod 2^{n+3}$.
   Therefore $3^{2^{n+1}} -1 \equiv 0 \mod 2^{n+3}$. By induction, the statement holds
   true.
*)

Require Import Arith.

Theorem numbertheory_3pow2pownm1mod2pownp3eq2pownp2:
  forall n : nat, 0 < n ->
  (3^(2^n) - 1) mod (2^(n + 3)) = 2^(n + 2).
Proof.
Admitted.