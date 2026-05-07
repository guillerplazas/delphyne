(* miniF2F problem: induction_11div10tonmn1ton
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any natural number $n$, we have $11\mid 10^n-(-1)^n$.

   Informal proof:
   We have that $10 \equiv -1 \mod 11$, so for every natural number $n$,
   $10^n \equiv (-1)^n \mod 11$. As a result, for every $n$ we have that $11$ divides
   $10^n - (-1)^n$.
*)

Require Import Arith ZArith Znumtheory.

Theorem induction_11div10tonmn1ton:
  forall n : nat,
  Z.divide 11 (Z.pow 10 (Z.of_nat n) - Z.pow (-1) (Z.of_nat n)).
Proof.
Admitted.
