(* miniF2F problem: mathd_algebra_33
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $2x = 5y$ and $7y = 10z$, what is the value of $\frac{z}{x}$ expressed as a common
   fraction? Show that it is \frac{7}{25}.

   Informal proof:
   $\frac{y}{x}=\frac25$ and $\frac{z}{y}=\frac{7}{10}$. Multiplying these, \[
   \frac25\cdot\frac{7}{10}=\frac y x\cdot\frac z y=\frac z x=\frac{7}{25}
   \]
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_33 :
  forall (x y z : R),
  x <> 0 ->
  2 * x = 5 * y ->
  7 * y = 10 * z ->
  z / x = 7 / 25.
Proof.
Admitted.