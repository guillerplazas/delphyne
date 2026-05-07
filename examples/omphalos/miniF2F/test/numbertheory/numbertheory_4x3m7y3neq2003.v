(* miniF2F problem: numbertheory_4x3m7y3neq2003
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that there are no integers $x$ and $y$ such that $4x^3 - 7y^3 = 2003$.

   Informal proof:
   We have that $2003 = 1 + 7 \times 286$. So $4x^3 - 7y^3 = 2003 \iff
   4x^3-1=7(y^3+286)$.
   We also observe that for every integer $x$, the rest of the division of $x^3$ by $7$
   is $0$, $1$, or $6$. So the rest of the division of $4x^3-1$ by $7$ is $6$, $3$, or
   $2$.
   As a result, $7$ does not divide $4x^3-1$, but since $7(y^3+286)$ is divisible by
   $7$, the equation cannot have integers solutions.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem numbertheory_4x3m7y3neq2003 : forall x y : Z,
  4 * x^3 - 7 * y^3 <> 2003.
Proof.
Admitted.