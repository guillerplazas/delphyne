(* miniF2F problem: algebra_2complexrootspoly_xsqp49eqxp7itxpn7i
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any complex number $x$, $x^2 + 49 = (x + 7i)(x - 7i)$.

   Informal proof:
   We have that $(x + 7i)(x - 7i) = x^2 + 7ix - 7ix - (7i)^2 = x^2 - 49 i^2$.
   Since $i^2=-1$, we have $(x + 7i)(x - 7i) = x^2+49$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_2complexrootspoly_xsqp49eqxp7itxpn7i :
  forall x : C,
  x^2 + 49 = (x + 7*Ci) * (x - 7*Ci).

Proof.
Admitted.
