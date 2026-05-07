(* miniF2F problem: amc12a_2019_p12
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Positive real numbers $x \neq 1$ and $y \neq 1$ satisfy $\log_2{x} = \log_y{16}$ and
   $xy = 64$. What is $(\log_2{\tfrac{x}{y}})^2$?

   $\textbf{(A) } \frac{25}{2} \qquad\textbf{(B) } 20 \qquad\textbf{(C) } \frac{45}{2}
   \qquad\textbf{(D) } 25 \qquad\textbf{(E) } 32$ Show that it is \textbf{(B) } 20.

   Informal proof:
   Let $\log_2{x} = \log_y{16}=k$, so that $2^k=x$ and $y^k=16 \implies
   y=2^{\frac{4}{k}}$. Then we have $(2^k)(2^{\frac{4}{k}})=2^{k+\frac{4}{k}}=2^6$.

   We therefore have $k+\frac{4}{k}=6$, and deduce $k^2-6k+4=0$. The solutions to this
   are $k = 3 \pm \sqrt{5}$. 

   To solve the problem, we now find 
   $\begin{align*}
   (\log_2\tfrac{x}{y})^2&=(\log_2 x - \log_2 y)^2\\
   &=(k-\tfrac{4}{k})^2=(3 \pm \sqrt{5} - \tfrac{4}{3 \pm \sqrt{5}})^2 \\
   &= (3 \pm \sqrt{5} - [3 \mp \sqrt{5}])^2\\
   &= (3 \pm \sqrt{5} - 3 \pm \sqrt{5})^2\\
   &=(\pm 2\sqrt{5})^2 \\
   &= \textbf{(B) } 20. \\
   \end{align*}$
   ~Edits by BakedPotato66
*)

Require Import Reals.
Require Import Psatz.

Open Scope R_scope.

Theorem amc12a_2019_p12:
  forall (x y : R),
  0 < x -> 0 < y ->
  (x <> 1) /\ (y <> 1) ->
  (ln x / ln 2 = ln 16 / ln y) ->
  (x * y = 64) ->
  (ln (x / y) / ln 2)^2 = 20.
Proof.
Admitted.
