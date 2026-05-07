(* miniF2F problem: algebra_manipexpr_apbeq2cceqiacpbceqm2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $a+b = 2c$ and $c = \text{Im}(1)$, show that $ac+bc=-2$.

   Informal proof:
   We have $ac + bc = (a+b)c=2c^2=2i^2=-2$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_manipexpr_apbeq2cceqiacpbceqm2:
  forall (a b c : C),
  a + b = 2 * c ->
  c = Ci ->
  a * c + b * c = -2.

Proof.
Admitted.
