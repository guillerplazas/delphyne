(* miniF2F problem: mathd_numbertheory_202
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the units digit of $19^{19}+99^{99}$? Show that it is 8.

   Informal proof:
   The units digit of a power of an integer is determined by the units digit of the
   integer; that is, the tens digit, hundreds digit, etc... of the integer have no
   effect on the units digit of the result. In this problem, the units digit of
   $19^{19}$ is the units digit of $9^{19}$. Note that $9^1=9$ ends in 9, $9^2=81$ ends
   in 1, $9^3=729$ ends in 9, and, in general, the units digit of odd powers of 9 is 9,
   whereas the units digit of even powers of 9 is 1. Since both exponents are odd, the
   sum of their units digits is $9+9=18$, the units digit of which is $8.$
*)

Require Import Coq.Arith.PeanoNat.

Theorem mathd_numbertheory_202 :
  (19^19 + 99^99) mod 10 = 8.
Proof.
Admitted.