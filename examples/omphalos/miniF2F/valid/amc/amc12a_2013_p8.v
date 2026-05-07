(* miniF2F problem: amc12a_2013_p8
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $x$ and $y$ are distinct nonzero real numbers such that $x+\tfrac{2}{x} =
   y + \tfrac{2}{y}$, what is $xy$?

   $ \textbf{(A)}\ \frac{1}{4}\qquad\textbf{(B)}\ \frac{1}{2}\qquad\textbf{(C)}\
   1\qquad\textbf{(D)}\ 2\qquad\textbf{(E)}\ 4\qquad $ Show that it is \textbf{(D) }{2}.

   Informal proof:
   $ x+\tfrac{2}{x}= y+\tfrac{2}{y} $

   Since $x\not=y$, we may assume that $x=\frac{2}{y}$ and/or, equivalently,
   $y=\frac{2}{x}$.

   Cross multiply in either equation, giving us $xy=2$.

   $\textbf{(D) }{2}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2013_p8:
  forall x y: R,
  x <> 0 ->
  y <> 0 ->
  x <> y ->
  x + 2 / x = y + 2 / y ->
  x * y = 2.
Proof.
Admitted.