(* miniF2F problem: numbertheory_x5neqy2p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any two integers $x$ and $y$, $x^5 \ne y^2 + 4$.

   Informal proof:
   We have that the remainder of the division of $x^5$ by $11$ is either $0$, $1$, or
   $10$: $x^5 \equiv k \mod 11$, with $k \in {0, 1, -1}$.
   Similarly, we observe that $y^2 \equiv k \mod 11$, with $k \in {0, 1, 3, 4, 5, -2}$.
   So $y^2 + 4 \equiv k \mod 11$, with $k \in {4, 5, 7, 8, 9, 2}$.
   As a result, $x^5$ and $y^2+4$ have different remainders when divided by $11$, and
   cannot be equal.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem numbertheory_x5neqy2p4:
  forall (x y : Z), x^5 <> y^2 + 4.
Proof.
Admitted.