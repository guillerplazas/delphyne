(* miniF2F problem: aime_1988_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $(\log_2 x)^2$ if $\log_2 (\log_8 x) = \log_8 (\log_2 x)$. Show that it is 027.

   Informal proof:
   Raise both as [[exponent]]s with base 8:

   $
   \begin{align*}
   8^{\log_2 (\log_8 x)} &= 8^{\log_8 (\log_2 x)}\\
   2^{3 \log_2(\log_8x)} &= \log_2x\\
   (\log_8x)^3 &= \log_2x\\
   \left(\frac{\log_2x}{\log_28}\right)^3 &= \log_2x\\
   (\log_2x)^2 &= (\log_28)^3 = 027\\
   \end{align*}
   $

   ----

   A quick explanation of the steps: On the 1st step, we use the property of
   [[logarithm]]s that $a^{\log_a x} = x$. On the 2nd step, we use the fact that $k
   \log_a x = \log_a x^k$. On the 3rd step, we use the [[change of base formula]], which
   states $\log_a b = \frac{\log_k b}{\log_k a}$ for arbitrary $k$.
*)

Require Import Coq.Reals.Reals.

Open Scope R_scope.


Definition logb (a x : R) : R := ln x / ln a.

Theorem aime_1988_p3 :
  forall (x : R),
    1 < x ->
    logb 2 (logb 8 x) = logb 8 (logb 2 x) ->
    (logb 2 x)^2 = 27.

Proof.
Admitted.
