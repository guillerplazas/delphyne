(* miniF2F problem: imo_1968_p5_1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ be a positive real number and $f$ be a real function such that $\forall x \in
   \mathbb{R}, f(x+a)=\frac{1}{2}+\sqrt{f(x)-f(x)^2}$.
   Show that there exists a positive real number $b$ such that $\forall x \in
   \mathbb{R}, f(x+b)=f(x)$.

   Informal proof:
   Since $f(x+a) \ge \frac{1}{2}$ is true for any $x$, and $f(x+a)(1-f(x+a)) =
   \frac{1}{4} - (f(x)-(f(x))^2) = (\frac{1}{2}-f(x))^2$

   We have:
   $f(x+2a) = \frac{1}{2} + \sqrt{(\frac{1}{2}-f(x))^2} = \frac{1}{2} + (f(x) -
   \frac{1}{2}) = f(x)$

   Therefore $f$ is periodic, with $2a>0$ as a period.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1968_p5_1 :
  forall (a : R) (f : R -> R),
  0 < a ->
  (forall x, f (x + a) = 1 / 2 + sqrt (f x - (f x)^2)) ->
  exists b : R, b > 0 /\ forall x, f (x + b) = f x.
Proof.
Admitted.