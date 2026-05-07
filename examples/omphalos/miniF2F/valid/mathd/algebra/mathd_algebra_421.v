(* miniF2F problem: mathd_algebra_421
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The parabolas defined by the equations $y=x^2+4x+6$ and $y=\frac{1}{2}x^2+x+6$
   intersect at points $(a,b)$ and $(c,d)$, where $c\ge a$. What is $c-a$? Show that it
   is 6.

   Informal proof:
   The graph of the two parabolas is shown below:

   [asy]
   Label f;

   f.p=fontsize(4);

   xaxis(-7,1,Ticks(f, 2.0));

   yaxis(0,25,Ticks(f, 5.0));
   real f(real x)

   {

   return x^2+4x+6;

   }

   draw(graph(f,-7,1),linewidth(1));
   real g(real x)

   {

   return .5x^2+x+6;

   }

   draw(graph(g,-7,1),linewidth(1));
   [/asy]

   The graphs intersect when $y$ equals both $x^2 + 4x +6$ and $\frac12x^2 + x+6$, so we
   have $x^2+4x+6=\frac{1}{2}x^2+x+6$. Combining like terms, we get
   $\frac{1}{2}x^2+3x=0$. Factoring out a $x$, we have $x(\frac{1}{2}x+3)=0$. So either
   $x=0$ or $\frac{1}{2}x+3=0\Rightarrow x=-6$, which are the two $x$ coordinates of the
   points of intersection. Thus, $c=0$ and $a=-6$, and $c-a=6$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_421 :
  forall (a b c d : R),
  b = a^2 + 4 * a + 6 ->
  b = (1 / 2) * a^2 + a + 6 ->
  d = c^2 + 4 * c + 6 ->
  d = (1 / 2) * c^2 + c + 6 ->
  a < c ->
  c - a = 6.
Proof.
Admitted.