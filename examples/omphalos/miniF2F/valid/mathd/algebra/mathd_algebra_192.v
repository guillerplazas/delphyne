(* miniF2F problem: mathd_algebra_192
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $Q = 11-5i$, $E = 11+5i$, and $D = 2i$, find $Q\cdot E \cdot D$. Show that it is
   292i.

   Informal proof:
   \begin{align*}
   QED &= (11-5i)(11+5i)2i\\
   &=2i(121-(5i)^2)\\
   &=2i(121+25)\\
   &=292i.
   \end{align*}
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_192
  (q e d : C)
  (h0 : q = 11 - 5 * Ci)
  (h1 : e = 11 + 5 * Ci)
  (h2 : d = 2 * Ci) :
  q * e * d = 292 * Ci.

Proof.
Admitted.
