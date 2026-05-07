(* miniF2F problem: mathd_numbertheory_30
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the remainder when $$33818^2 + 33819^2 + 33820^2 + 33821^2 + 33822^2$$is divided
   by 17. Show that it is 0.

   Informal proof:
   Reducing each number modulo 17, we get \begin{align*}
   &33818^2 + 33819^2 + 33820^2 + 33821^2 + 33822^2\\
   &\qquad\equiv 5^2 + 6^2 + 7^2 + 8^2 + 9^2 \\
   &\qquad\equiv 255 \\
   &\qquad\equiv 0 \pmod{17}.
   \end{align*}
*)

Require Import Arith.
Require Import ZArith.

Open Scope Z_scope.

Theorem mathd_numbertheory_30:
  (33818^2 + 33819^2 + 33820^2 + 33821^2 + 33822^2) mod 17 = 0.
Proof.
Admitted.