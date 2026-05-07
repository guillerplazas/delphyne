(* miniF2F problem: algebra_2rootspoly_apatapbeq2asqp2ab
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any complex numbers $a$ and $b$, $(a+a)(a+b) = 2a^2 + 2ab$.

   Informal proof:
   By expanding, we get $(a+a)(a+b)=(a+a)a+(a+a)b$. Since $(a+a)a+(a+a)b = (a^2 + a^2) +
   (ab + ab)$, we get $(a+a)(a+b) = 2a^2 + 2ab$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_2rootspoly_apatapbeq2asqp2ab :
  forall (a b : C), (a + a) * (a + b) = 2 * (a ^ 2) + 2 * (a * b).



Proof.
Admitted.
