(* miniF2F problem: aime_1991_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find $x^2+y^2_{}$ if $x_{}^{}$ and $y_{}^{}$ are positive integers such that
   $\begin{align*}
   xy+x+y&=71, \\
   x^2y+xy^2&=880.
   \end{align*}$ Show that it is 146.

   Informal proof:
   Define $a = x + y$ and $b = xy$. Then $a + b = 71$ and $ab = 880$. Solving these two
   equations yields a [[quadratic equation|quadratic]]: $a^2 - 71a + 880 = 0$, which
   [[factor]]s to $(a - 16)(a - 55) = 0$. Either $a = 16$ and $b = 55$ or $a = 55$ and
   $b = 16$. For the first case, it is easy to see that $(x,y)$ can be $(5,11)$ (or vice
   versa). In the second case, since all factors of $16$ must be $\le 16$, no two
   factors of $16$ can sum greater than $32$, and so there are no integral solutions for
   $(x,y)$. The solution is $5^2 + 11^2 = 146$.
*)

Theorem aime_1991_p1 :
  forall (x y : nat),
    (x * y + x + y = 71) ->
    (x*x * y + x * y*y = 880) ->
    (x*x + y*y = 146).
Proof.
Admitted.
