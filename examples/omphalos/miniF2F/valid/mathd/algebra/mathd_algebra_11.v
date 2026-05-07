(* miniF2F problem: mathd_algebra_11
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the simplified numerical value of $\frac{a+11b}{a-b}$ if
   $\frac{4a+3b}{a-2b}=5$? Show that it is 2.

   Informal proof:
   Let's play with the given condition a little. Clearing out the denominator gives
   $4a+3b=5(a-2b)=5a-10b$. Selectively combine like terms by adding $9b-4a$ to both
   sides to get $12b=a-b$. This gives $\dfrac{12b}{a-b}=1$.

   Now, we want to find $\dfrac{a+11b}{a-b}$. Rewrite this as
   $\dfrac{a-b+12b}{a-b}=\dfrac{a-b}{a-b}+\dfrac{12b}{a-b}=1+1=2$, and we are done.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_11:
  forall (a b : R),
    a <> b ->
    a <> 2 * b ->
    (4 * a + 3 * b) / (a - 2 * b) = 5 ->
    (a + 11 * b) / (a - b) = 2.
Proof.
Admitted.