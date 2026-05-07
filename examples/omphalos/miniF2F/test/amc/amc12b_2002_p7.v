(* miniF2F problem: amc12b_2002_p7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The product of three consecutive positive integers is $8$ times their sum. What is
   the sum of their [[perfect square|squares]]?

   $\mathrm{(A)}\ 50
   \qquad\mathrm{(B)}\ 77
   \qquad\mathrm{(C)}\ 110
   \qquad\mathrm{(D)}\ 149
   \qquad\mathrm{(E)}\ 194$ Show that it is \mathrm{ (B)}\ 77.

   Informal proof:
   Let the three consecutive positive integers be $a-1$, $a$, and $a+1$. Since the mean
   is $a$, the sum of the integers is $3a$. So $8$ times the sum is just $24a$. With
   this, we now know that $a(a-1)(a+1)=24a\Rightarrow(a-1)(a+1)=24$.  $24=4\times6$, so
   $a=5$. Hence, the sum of the squares is $4^2+5^2+6^2=\mathrm{ (B)}\ 77$.
*)

Require Import Arith.

Theorem amc12b_2002_p7 :
  forall a b c : nat,
  (0 < a) -> (0 < b) -> (0 < c) ->
  (b = a + 1) ->
  (c = b + 1) ->
  (a * b * c = 8 * (a + b + c)) ->
  (a^2 + b^2 + c^2 = 77).
Proof.
Admitted.