(* miniF2F problem: amc12b_2002_p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $n$ be a positive [[integer]] such that $\frac 12 + \frac 13 + \frac 17 + \frac
   1n$ is an integer. Which of the following statements is '''not ''' true:

   $\mathrm{(A)}\ 2\ \text{divides\ }n
   \qquad\mathrm{(B)}\ 3\ \text{divides\ }n
   \qquad\mathrm{(C)}$ $\ 6\ \text{divides\ }n 
   \qquad\mathrm{(D)}\ 7\ \text{divides\ }n
   \qquad\mathrm{(E)}\ n > 84$ Show that it is \mathrm{(E)}\ n>84.

   Informal proof:
   Since $\frac 12 + \frac 13 + \frac 17  = \frac {41}{42}$, $0 < \lim_{n \rightarrow
   \infty} \left(\frac{41}{42} + \frac{1}{n}\right) < \frac {41}{42} + \frac 1n <
   \frac{41}{42} + \frac 11 < 2$

   From which it follows that $\frac{41}{42} + \frac 1n = 1$ and $n = 42$. The only
   answer choice that is not true is $\mathrm{(E)}\ n>84$.
*)

Require Import Reals.
Require Import ZArith.
Require Import Reals.Rfunctions.
Require Import Lia.

Open Scope R_scope.

Theorem amc12b_2002_p4 :
  forall (n : nat),
    (n > 0)%nat ->
    exists k : Z, 
      (1/2 + 1/3 + 1/7 + 1/(INR n))%R = IZR k ->
      n = 42%nat.



Proof.
Admitted.
