(* miniF2F problem: aime_1983_p1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $x$, $y$ and $z$ all exceed $1$ and let $w$ be a positive number such that
   $\log_x w = 24$, $\log_y w = 40$ and $\log_{xyz} w = 12$. Find $\log_z w$. Show that
   it is 060.

   Informal proof:
   The [[logarithm]]ic notation doesn't tell us much, so we'll first convert everything
   to the equivalent exponential forms.

   $x^{24}=w$, $y^{40}=w$, and $(xyz)^{12}=w$. If we now convert everything to a power
   of $120$, it will be easy to isolate $z$ and $w$.

   $x^{120}=w^5$, $y^{120}=w^3$, and $(xyz)^{120}=w^{10}$.

   With some substitution, we get $w^5w^3z^{120}=w^{10}$ and $\log_zw=060$.
*)

Require Import Coq.Reals.Reals.

Open Scope R_scope.

Theorem aime_1983_p1 :
  forall (x y z w : R),
    1 < x ->
    1 < y ->
    1 < z ->
    0 < w ->
    ln w / ln x = 24 ->
    ln w / ln y = 40 ->
    ln w / ln (x * y * z) = 12 ->
    ln w / ln z = 60.

Proof.
Admitted.
