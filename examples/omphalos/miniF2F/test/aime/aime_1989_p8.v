(* miniF2F problem: aime_1989_p8
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Assume that $x_1,x_2,\ldots,x_7$ are real numbers such that
   $\begin{align*}
   x_1 + 4x_2 + 9x_3 + 16x_4 + 25x_5 + 36x_6 + 49x_7 &= 1, \\
   4x_1 + 9x_2 + 16x_3 + 25x_4 + 36x_5 + 49x_6 + 64x_7 &= 12, \\
   9x_1 + 16x_2 + 25x_3 + 36x_4 + 49x_5 + 64x_6 + 81x_7 &= 123.
   \end{align*}$
   Find the value of $16x_1+25x_2+36x_3+49x_4+64x_5+81x_6+100x_7$. Show that it is 334.

   Informal proof:
   Note that each given equation is of the form
   $f(k)=k^2x_1+(k+1)^2x_2+(k+2)^2x_3+(k+3)^2x_4+(k+4)^2x_5+(k+5)^2x_6+(k+6)^2x_7$ for
   some $k\in\{1,2,3\}.$

   When we expand $f(k)$ and combine like terms, we obtain a quadratic function of $k:$
   $f(k)=ak^2+bk+c,$ where $a,b,$ and $c$ are linear combinations of
   $x_1,x_2,x_3,x_4,x_5,x_6,$ and $x_7.$ 

   We are given that
   $\begin{alignat*}{10}
   f(1)&=\phantom{42}a+b+c&&=1, \\
   f(2)&=4a+2b+c&&=12, \\
   f(3)&=9a+3b+c&&=123,
   \end{alignat*}$
   and we wish to find $f(4).$

   We eliminate $c$ by subtracting the first equation from the second, then subtracting
   the second equation from the third:
   $\begin{align*}
   3a+b&=11, \\
   5a+b&=111.
   \end{align*}$
   By either substitution or elimination, we get $a=50$ and $b=-139.$ Substituting these
   back produces $c=90.$

   Finally, the answer is $f(4)=16a+4b+c=334.$

   ~Azjps
*)

Require Import Reals.
Open Scope R_scope.

Theorem aime_1989_p8 :
  forall a b c d e f g : R,
    a + 4 * b + 9 * c + 16 * d + 25 * e + 36 * f + 49 * g = 1 ->
    4 * a + 9 * b + 16 * c + 25 * d + 36 * e + 49 * f + 64 * g = 12 ->
    9 * a + 16 * b + 25 * c + 36 * d + 49 * e + 64 * f + 81 * g = 123 ->
    16 * a + 25 * b + 36 * c + 49 * d + 64 * e + 81 * f + 100 * g = 334.
Proof.
Admitted.