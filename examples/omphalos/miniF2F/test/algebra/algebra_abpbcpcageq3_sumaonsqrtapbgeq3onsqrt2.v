(* miniF2F problem: algebra_abpbcpcageq3_sumaonsqrtapbgeq3onsqrt2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For positive real numbers a, b, c, such that $3 \leq ab+bc+ca$, show that $3/\sqrt{2}
   \leq a/\sqrt{a+b} + b/\sqrt{b+c} + c/\sqrt{c+a}$.

   Informal proof:
   From Holder's inequality, we have $(\sum \frac{a}{\sqrt{a+b}})^{2/3} (\sum
   a(a+b))^{1/3} \geq \sum a$.
   Hence $\sum \frac{a}{\sqrt{a+b}} \geq \frac{(\sum a)^{3/2}}{(\sum a(a+b))^{1/2}}$. It
   thus suffices to prove $\frac{(\sum a)^3}{\sum a(a+b)} \geq \frac{9}{2}$, which is
   equivalent to $2(\sum a)^3 \geq 9 (\sum a^2 + \sum ab)$.

   Let $p=\sum a$ and $q=\sum ab$. From the assumption we know that $q \geq 3$. The
   inequality becomes $2p^3\geq 9(p^2-q)$, which is equivalent to $2p^3+9q\geq 9p^2$. By
   the AM-GM inequality, we have $2p^3 + 9q\geq 2p^3 + 27 = p^3 + p^3 + 27 \geq
   3*(p^3*p^3*27)^{1/3} = 9p^2$. Hence the inequality holds.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_abpbcpcageq3_sumaonsqrtapbgeq3onsqrt2:
  forall a b c : R,
  0 < a -> 0 < b -> 0 < c -> 
  3 <= a * b + b * c + c * a ->
  3 / sqrt 2 <= a / sqrt (a + b) + b / sqrt (b + c) + c / sqrt (c + a).
Proof.
Admitted.