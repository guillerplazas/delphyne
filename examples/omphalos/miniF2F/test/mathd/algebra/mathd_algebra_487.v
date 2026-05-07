(* miniF2F problem: mathd_algebra_487
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the distance between the two intersections of $y=x^2$ and $x+y=1$? Show that
   it is \sqrt{10}.

   Informal proof:
   To find the $x$-coordinates of the intersections, substitute $x^2$ for $y$ in $x+y=1$
   and solve for $x$, resulting in  \begin{align*}
   x+x^2&=1 \\
   \Rightarrow \qquad x^2+x-1&=0 \\
   \Rightarrow \qquad x&=\frac{-1\pm\sqrt{1+4}}2=\frac{-1\pm\sqrt5}2\\
   \end{align*}Using each of these coordinates to solve for $y$ gives us the
   intersections at $\left(\frac{-1+\sqrt5}2,\frac{3-\sqrt5}2\right)$ and
   $\left(\frac{-1-\sqrt5}2,\frac{3+\sqrt5}2\right)$.  Using the distance formula, we
   have \begin{align*}
   &\sqrt{ \left(\frac{-1+\sqrt5}{2}-\frac{-1-\sqrt5}{2}\right)^2 +
   \left(\frac{3-\sqrt5}2-\frac{3+\sqrt5}2\right)^2 }\\
   &\qquad=\sqrt{\left(\frac{2\sqrt5}2\right)^2 + \left(-\frac{2\sqrt5}2\right)^2}\\
   &\qquad=\sqrt{ 2\sqrt5^2 }\\
   &\qquad=\sqrt{10}.
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_487
  (a b c d : R)
  (h₀ : b = a^2)
  (h₁ : a + b = 1)
  (h₂ : d = c^2)
  (h₃ : c + d = 1)
  (h₄ : a <> c) :
  sqrt ((a - c)^2 + (b - d)^2) = sqrt 10.
Proof.
Admitted.
