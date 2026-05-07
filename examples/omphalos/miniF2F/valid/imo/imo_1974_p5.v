(* miniF2F problem: imo_1974_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Determine all possible values of $S =
   \frac{a}{a+b+d}+\frac{b}{a+b+c}+\frac{c}{b+c+d}+\frac{d}{a+c+d}$ where $a, b, c, d,$
   are arbitrary positive numbers.

   Informal proof:
   Note that $2 = \frac{a}{a+b}+\frac{b}{a+b}+\frac{c}{c+d}+\frac{d}{c+d} > S >
   \frac{a}{a+b+c+d}+\frac{b}{a+b+c+d}+\frac{c}{a+b+c+d}+\frac{d}{a+b+c+d} = 1.$ We will
   now prove that $S$ can reach any range in between $1$ and $2$.

   Choose any positive number $a$. For some variables such that $k, m, l > 0$ and $k + m
   + l = 1$, let $b = ak$, $c = am$, and $d = al$. Plugging this back into the original
   fraction, we get 
   $S = \frac{a}{a+ak+al}+\frac{ak}{a+ak+am}+\frac{am}{ak+am+al}+\frac{al}{a+am+al} =
   \frac{1}{1+k+l}+\frac{k}{1+k+m}+\frac{m}{k+m+l}+\frac{l}{1+m+l}.$
   The above equation can be further simplified to 
   $S = \frac{1}{2-m}+\frac{k}{2-l}+m+\frac{l}{2-k}.$
   Note that $S$ is a continuous function and that $f(m) = m + \frac{1}{2-m}$ is a
   strictly increasing function. We can now decrease $k$ and $l$ to make $m$ tend
   arbitrarily close to $1$. We see $\lim_{m\to1} m + \frac{1}{2-m} = 2$, meaning $S$
   can be brought arbitrarily close to $2$. 
   Now, set $a = d = x$ and $b = c = y$ for some positive real numbers $x, y$. Then 
   $S = \frac{2x}{2x+y} + \frac{2y}{2y+x} = \frac{2y^2 + 8xy + 2x^2}{2y^2 + 5xy +
   2x^2}.$
   Notice that if we treat the numerator and denominator each as a quadratic in $y$, we
   will get $1 + \frac{g(x)}{2y^2 + 5xy + 2x^2}$, where $g(x)$ has a degree lower than
   $2$. This means taking $\lim_{y\to\infty} 1 + \frac{g(x)}{2y^2 + 5xy + 2x^2} = 1$,
   which means $S$ can be brought arbitrarily close to $1$. Therefore, we are done.
   $ $
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1974_p5 :
  forall (a b c d s : R),
  (0 < a) -> (0 < b) -> (0 < c) -> (0 < d) ->
  (s = a / (a + b + d) + b / (a + b + c) + c / (b + c + d) + d / (a + c + d)) ->
  (1 < s) /\ (s < 2).
Proof.
Admitted.