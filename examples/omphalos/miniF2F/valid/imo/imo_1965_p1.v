(* miniF2F problem: imo_1965_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Determine all values $x$ in the interval $0\leq x\leq 2\pi $ which satisfy the
   inequality
   $2\cos x \leq \left| \sqrt{1+\sin 2x} - \sqrt{1-\sin 2x } \right| \leq \sqrt{2}.$

   Informal proof:
   We shall deal with the left side of the inequality first ($2\cos x \leq \left|
   \sqrt{1+\sin 2x} - \sqrt{1-\sin 2x } \right| $) and the right side after that.

   It is clear that the left inequality is true when $\cos x$ is non-positive, and that
   is when $x$ is in the interval $[\pi/2, 3\pi/2]$. We shall now consider when $\cos x$
   is positive. We can square the given inequality, and the resulting inequality will be
   true whenever the original left inequality is true. $4\cos^2{x}\leq 1+\sin 2x+1-\sin
   2x-2\sqrt{1-\sin^2 2x}=2-2\sqrt{\cos^2{2x}}$. This inequality is equivalent to
   $2\cos^2 x\leq 1-\left| \cos 2x\right|$. I shall now divide this problem into cases.

   Case 1: $\cos 2x$ is non-negative. This means that $x$ is in one of the intervals
   $[0,\pi/4]$ or $[7\pi/4, 2\pi]$. We must find all $x$ in these two intervals such
   that $2\cos^2 x\leq 1-\cos 2x$. This inequality is equivalent to $2\cos^2 x\leq
   2\sin^2 x$, which is only true when $x=\pi/4$ or $7\pi/4$.

   Case 2: $\cos 2x$ is negative. This means that $x$ is in one of the interavals
   $(\pi/4, \pi/2)$ or $(3\pi/2, 7\pi/4)$. We must find all $x$ in these two intervals
   such that $2\cos^2 x\leq 1+\cos 2x$, which is equivalent to $2\cos^2 x\leq 2\cos^2
   x$, which is true for all $x$ in these intervals.

   Therefore the left inequality is true when $x$ is in the union of the intervals
   $[\pi/4, \pi/2)$, $(3\pi/2, 7\pi/4]$, and $[\pi/2, 3\pi/2]$, which is the interval
   $[\pi/4, 7\pi/4]$. We shall now deal with the right inequality.

   As above, we can square it and have it be true whenever the original right inequality
   is true, so we do that. $2-2\sqrt{\cos^2{2x}}\leq 2$, which is always true. Therefore
   the original right inequality is always satisfied, and all $x$ such that the original
   inequality is satisfied are in the interval $[\pi/4, 7\pi/4]$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem imo_1965_p1 :
  forall (x : R),
    0 <= x ->
    x <= 2 * PI ->
    2 * cos x <= Rabs (sqrt (1 + sin (2 * x)) - sqrt (1 - sin (2 * x))) ->
    Rabs (sqrt (1 + sin (2 * x)) - sqrt (1 - sin (2 * x))) <= sqrt 2 ->
    PI / 4 <= x /\ x <= 7 * PI / 4.

Proof.
Admitted.
