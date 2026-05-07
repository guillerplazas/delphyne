(* miniF2F problem: aime_1990_p15
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $ax^5 + by^5$ if the real numbers $a,b,x,$ and $y$ satisfy the equations
   $\begin{align*}
   ax + by &= 3, \\
   ax^2 + by^2 &= 7, \\
   ax^3 + by^3 &= 16, \\
   ax^4 + by^4 &= 42.
   \end{align*}$ Show that it is 020.

   Informal proof:
   Set $S = (x + y)$ and $P = xy$. Then the relationship

   $(ax^n + by^n)(x + y) = (ax^{n + 1} + by^{n + 1}) + (xy)(ax^{n - 1} + by^{n - 1})$

   can be exploited:

   $\begin{eqnarray*}(ax^2 + by^2)(x + y) & = & (ax^3 + by^3) + (xy)(ax + by) \\
   (ax^3 + by^3)(x + y) & = & (ax^4 + by^4) + (xy)(ax^2 + by^2)\end{eqnarray*}$

   Therefore:

   $\begin{eqnarray*}7S & = & 16 + 3P \\
   16S & = & 42 + 7P\end{eqnarray*}$

   Consequently, $S = - 14$ and $P = - 38$. Finally:

   $\begin{eqnarray*}(ax^4 + by^4)(x + y) & = & (ax^5 + by^5) + (xy)(ax^3 + by^3) \\
   (42)(S) & = & (ax^5 + by^5) + (P)(16) \\
   (42)( - 14) & = & (ax^5 + by^5) + ( - 38)(16) \\
   ax^5 + by^5 & = & 020\end{eqnarray*}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem aime_1990_p15 :
  forall (a b x y : R),
  (a * x + b * y = 3) ->
  (a * x^2 + b * y^2 = 7) ->
  (a * x^3 + b * y^3 = 16) ->
  (a * x^4 + b * y^4 = 42) ->
  (a * x^5 + b * y^5 = 20).
Proof.
Admitted.