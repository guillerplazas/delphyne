(* miniF2F problem: imo_1973_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be real numbers for which the equation
   $x^4 + ax^3 + bx^2 + ax + 1 = 0$
   has at least one real solution. For all such pairs $(a, b)$, find the minimum value
   of $a^2 + b^2$.

   Informal proof:
   Substitute $z=x+1/x$ to change the original equation into $z^2+az+b-2=0$. This
   equation has solutions $z=\frac{-a \pm \sqrt{a^2+8-4b}}{2}$. We also know that
   $|z|=|x+1/x| \geq 2$. So,

   $\left | \frac{-a \pm \sqrt{a^2+8-4b}}{2} \right | \geq 2$

   $\frac{|a|+\sqrt{a^2+8-4b}}{2} \geq 2$

   $|a|+\sqrt{a^2+8-4b} \geq 4$

   Rearranging and squaring both sides,

   $a^2+8-4b \geq a^2-16|a|+16$

   $2|a|-b \geq 2$

   So, $a^2+b^2 \geq a^2+(2-2|a|)^2 = 5a^2-8|a|+4 = 5(|a|-\frac{4}{5})^2+\frac{4}{5}$.

   Therefore, the smallest possible value of $a^2+b^2$ is $\frac{4}{5}$, when $a=\pm
   \frac{4}{5}$ and $b=\frac{-2}{5}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1973_p3 :
  forall (a b : R),
  (exists x : R, x^4 + a * x^3 + b * x^2 + a * x + 1 = 0) ->
  4/5 <= a^2 + b^2.
Proof.
Admitted.