(* miniF2F problem: numbertheory_xsqpysqintdenomeq
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $x$ and $y$ be rational numbers. Show that if $x^2 + y^2$ is an integer, then $x$
   and $y$ have the same denominator.

   Informal proof:
   Write $x=\frac{a}{b}$ with $b>0$ and $gcd(a,b)=1$ and $y=\frac{c}{d}$ with $d>0$ and
   $gcd(c,d)=1$. Since $x^2+y^2 = \frac{a^2d^2+c^2b^2}{b^2d^2}$ is an integer, there is
   an integer $k$ such that $k(b^2d^2) = (a^2d^2+c^2b^2)$.
   Thus, $b^2(kd^2-c^2)=a^2d^2$ and  $d^2(kd^2-a^2)=c^2b^2$. In particular, $b^2\mid
   a^2d^2$ and $d^2\mid c^2b^2$.
   Since $gcd(a,b)=gcd(c,d)=1$, this means $b^2 \mid d^2$ and $d^2\mid b^2$. As $b>0$
   and $d>0$, we conclude that $b=d$, thus $x$ and $y$ share the same denominator.
*)

Require Import QArith.
Require Import Reals.

Theorem numbertheory_xsqpysqintdenomeq:
  forall (x y : Q),
  Qden (x * x + y * y) = 1%positive ->
  Qden x = Qden y.
Proof.
Admitted.