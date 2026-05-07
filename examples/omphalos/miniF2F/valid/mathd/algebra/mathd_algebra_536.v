(* miniF2F problem: mathd_algebra_536
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Simplify: $3!(2^3+\sqrt{9})\div 2$. Show that it is 33.

   Informal proof:
   Simplify according to the order of operations. \begin{align*}
   3!(2^3+\sqrt{9})\div 2 &= 6(8+3)\div 2 \\
   &=6(11)\div 2 \\
   &=66\div 2\\
   &=33.
   \end{align*}
*)

Require Import Reals.
Require Import Arith.Factorial.

Open Scope R_scope.

Theorem mathd_algebra_536:
  INR (fact 3) * (2^3 + sqrt 9) / 2 = 33.
Proof.
Admitted.