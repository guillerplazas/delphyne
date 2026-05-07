(* miniF2F problem: aime_1984_p1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the value of $a_2+a_4+a_6+a_8+\ldots+a_{98}$ if $a_1$, $a_2$, $a_3\ldots$ is an
   [[arithmetic progression]] with common difference 1, and
   $a_1+a_2+a_3+\ldots+a_{98}=137$. Show that it is 093.

   Informal proof:
   One approach to this problem is to apply the formula for the sum of an [[arithmetic
   series]] in order to find the value of $a_1$, then use that to calculate $a_2$ and
   sum another arithmetic series to get our answer.

   A somewhat quicker method is to do the following: for each $n \geq 1$, we have $a_{2n
   - 1} = a_{2n} - 1$.  We can substitute this into our given equation to get $(a_2 - 1)
   + a_2 + (a_4 - 1) + a_4 + \ldots + (a_{98} - 1) + a_{98} = 137$.  The left-hand side
   of this equation is simply $2(a_2 + a_4 + \ldots + a_{98}) - 49$, so our desired
   value is $\frac{137 + 49}{2} = 093$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem aime_1984_p1 :
  forall (u : nat -> R),
  (forall n, u (n + 1)%nat = u n + 1) ->
  sum_f_R0 (fun k => u (k + 1)%nat) 97 = 137 ->
  sum_f_R0 (fun k => u (2 * (k + 1))%nat) 48 = 93.
Proof.
Admitted.
