(* miniF2F problem: mathd_algebra_234
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sixth term in the geometric sequence $\frac{27}{125}, \frac{9}{25},
   \frac{3}{5},\ldots$?  Express your answer as a common fraction. Show that it is
   \frac{25}{9}.

   Informal proof:
   With common ratio $\frac{5}{3}$, and first term $\frac{27}{125}$, we simply take:
   $\frac{27}{125}\times\left(\frac{5}{3}\right)^{5}$ which yields $\frac{25}{9}.$
*)

Require Import Reals.
Require Import Rfunctions.
Require Import Rbasic_fun.

Open Scope R_scope.

Theorem mathd_algebra_234 :
  forall d : R,
  27/125 * d = 9/25 ->
  3/5 * (d^3) = 25/9.
Proof.
Admitted.