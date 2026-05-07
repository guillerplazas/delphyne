(* miniF2F problem: amc12b_2002_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of  $(3x - 2)(4x + 1) - (3x - 2)4x + 1$ when $x=4$?

   $\mathrm{(A)}\ 0
   \qquad\mathrm{(B)}\ 1
   \qquad\mathrm{(C)}\ 10
   \qquad\mathrm{(D)}\ 11
   \qquad\mathrm{(E)}\ 12$ Show that it is \mathrm{(D)}\ 11.

   Informal proof:
   By the distributive property, 

   $(3x-2)[(4x+1)-4x] + 1 = 3x-2 + 1 = 3x-1 = 3(4) - 1 = \mathrm{(D)}\ 11$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem amc12b_2002_p2 (x : Z) (h0 : x = 4) :
  (3 * x - 2) * (4 * x + 1) - (3 * x - 2) * (4 * x) + 1 = 11.
Proof.
Admitted.