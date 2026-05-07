(* miniF2F problem: algebra_2rootsintpoly_am10tap11eqasqpam110
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any complex number $a$, $(a-10)(a+11)=a^2+a-110$.

   Informal proof:
   By expanding, we get $(a-10)(a+11) = a^2 - 10a + 11a - 10 \times 11$. After
   simplification, we have that $(a-10)(a+11)=a^2+a-110$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_2rootsintpoly_am10tap11eqasqpam110
  (a : C) :
  (a - 10) * (a + 11) = a^2 + a - 110.

Proof.
Admitted.
