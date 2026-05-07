(* miniF2F problem: aime_1995_p7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $(1+\sin t)(1+\cos t)=5/4$ and
   :$(1-\sin t)(1-\cos t)=\frac mn-\sqrt{k},$
   where $k, m,$ and $n_{}$ are [[positive integer]]s with $m_{}$ and $n_{}$
   [[relatively prime]], find $k+m+n.$ Show that it is 027.

   Informal proof:
   From the givens, 
   $2\sin t \cos t + 2 \sin t + 2 \cos t = \frac{1}{2}$, and adding $\sin^2 t + \cos^2t
   = 1$ to both sides gives $(\sin t + \cos t)^2 + 2(\sin t + \cos t) = \frac{3}{2}$. 
   Completing the square on the left in the variable $(\sin t + \cos t)$ gives $\sin t +
   \cos t = -1 \pm \sqrt{\frac{5}{2}}$.  Since $|\sin t + \cos t| \leq \sqrt 2 < 1 +
   \sqrt{\frac{5}{2}}$, we have $\sin t + \cos t = \sqrt{\frac{5}{2}} - 1$.  Subtracting
   twice this from our original equation gives $(\sin t - 1)(\cos t - 1) = \sin t \cos t
   - \sin t - \cos t + 1 = \frac{13}{4} - \sqrt{10}$, so the answer is $13 + 4 + 10 =
   027$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem aime_1995_p7 :
  forall (k m n : nat) (t : R),
  (0 < k)%nat -> (0 < m)%nat -> (0 < n)%nat ->
  (Nat.gcd m n = 1)%nat ->
  (1 + sin t) * (1 + cos t) = 5 / 4 ->
  (1 - sin t) * (1 - cos t) = INR m / INR n - sqrt (INR k) ->
  (k + m + n = 27)%nat.
Proof.
Admitted.
