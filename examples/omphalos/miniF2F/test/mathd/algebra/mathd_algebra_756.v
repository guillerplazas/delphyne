(* miniF2F problem: mathd_algebra_756
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given $2^a = 32$ and $a^b = 125$ find $b^a$. Show that it is 243.

   Informal proof:
   We note that $32 = 2 \cdot 2\cdot 2\cdot 2\cdot 2= 2^5$, so $a=5$. This leaves us
   with $5^b=125=5\cdot5\cdot5=5^3$, which means that $b=3$. Therefore our answer is
   $b^a = 3^5 = 243$.
*)

Require Import Reals.

Theorem mathd_algebra_756 :
  forall (a b : R),
  Rpower 2 a = IZR 32 ->
  Rpower a b = IZR 125 ->
  Rpower b a = IZR 243.

Proof.
Admitted.
