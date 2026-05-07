(* miniF2F problem: amc12b_2002_p6
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $a$ and $b$ are nonzero real numbers, and that the [[equation]] $x^2 +
   ax + b = 0$ has solutions $a$ and $b$. Then the pair $(a,b)$ is

   $\mathrm{(A)}\ (-2,1)
   \qquad\mathrm{(B)}\ (-1,2)
   \qquad\mathrm{(C)}\ (1,-2)
   \qquad\mathrm{(D)}\ (2,-1)
   \qquad\mathrm{(E)}\ (4,4)$ Show that it is \mathrm{(C)}\ (1,-2).

   Informal proof:
   Since $(x-a)(x-b) = x^2 - (a+b)x + ab = x^2 + ax + b = 0$, it follows by comparing
   [[coefficient]]s that $-a - b = a$ and that $ab = b$. Since $b$ is nonzero, $a = 1$,
   and $-1 - b = 1 \Longrightarrow b = -2$. Thus $(a,b) = \mathrm{(C)}\ (1,-2)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2002_p6 :
  forall a b : R,
  (a <> 0) /\ (b <> 0) ->
  (forall x, x^2 + a * x + b = (x - a) * (x - b)) ->
  a = 1 /\ b = -2.
Proof.
Admitted.