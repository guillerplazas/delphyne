(* miniF2F problem: mathd_algebra_304
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Compute $91^2$ in your head. Show that it is 8281.

   Informal proof:
   Note that $91\times 91 = (90 + 1)^2 = 90^2 + 2\cdot 90 + 1 = 8100 + 180 + 1 = 8281$.
*)

Require Import Nat.
Require Import ZArith.

Theorem mathd_algebra_304:
  91^2 = 8281.
Proof.
Admitted.