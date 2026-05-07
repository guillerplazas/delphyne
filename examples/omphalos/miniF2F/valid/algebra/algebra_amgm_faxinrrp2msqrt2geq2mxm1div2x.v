(* miniF2F problem: algebra_amgm_faxinrrp2msqrt2geq2mxm1div2x
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $x$ be a positive real number. Show that $2 - \sqrt{2} \geq 2 - x -
   \frac{1}{2x}$.

   Informal proof:
   The statement is equivalent to showing $x+\frac{1}{2x} \geq \sqrt{2}$. By AM-GM, $x +
   \frac{1}{2x} \geq 2\sqrt{\frac{x}{2x}} = \sqrt{2}.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_amgm_faxinrrp2msqrt2geq2mxm1div2x :
  forall x : R, x > 0 -> 2 - sqrt 2 >= 2 - x - 1 / (2 * x).
Proof.
Admitted.