(* miniF2F problem: amc12a_2003_p5
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of the two 5-digit numbers $AMC10$ and $AMC12$ is $123422$. What is $A+M+C$? 

   $ \mathrm{(A) \ } 10\qquad \mathrm{(B) \ } 11\qquad \mathrm{(C) \ } 12\qquad
   \mathrm{(D) \ } 13\qquad \mathrm{(E) \ } 14 $ Show that it is \mathrm{(E)}\ 14.

   Informal proof:
   $AMC10+AMC12=123422$

   $AMC00+AMC00=123400$ 

   $AMC+AMC=1234$

   $2\cdot AMC=1234$ 

   $AMC=\frac{1234}{2}=617$

   Since $A$, $M$, and $C$ are digits, $A=6$, $M=1$, $C=7$. 

   Therefore, $A+M+C = 6+1+7 = \mathrm{(E)}\ 14 $.
*)

Require Import Nat.

Theorem amc12a_2003_p5 :
  forall (A M C : nat),
  (A <= 9 /\ M <= 9 /\ C <= 9) ->
  (10000 * A + 1000 * M + 100 * C + 10 * 1 + 0) + 
  (10000 * A + 1000 * M + 100 * C + 10 * 1 + 2) = 123422 ->
  A + M + C = 14.
Proof.
Admitted.