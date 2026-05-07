(* miniF2F problem: amc12_2001_p9
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f$ be a function satisfying $f(xy) = \frac{f(x)}y$ for all positive real numbers
   $x$ and $y$. If $f(500) =3$, what is the value of $f(600)$?

   $(\mathrm{A})\ 1 \qquad (\mathrm{B})\ 2 \qquad (\mathrm{C})\ \frac52 \qquad
   (\mathrm{D})\ 3 \qquad (\mathrm{E})\ \frac{18}5$ Show that it is \textbf{C } \frac52.

   Informal proof:
   Letting $x = 500$ and $y = \dfrac65$ in the given equation, we get
   $f(500\cdot\frac65) = \frac3{\frac65} = \frac52$, or $f(600) = \textbf{C } \frac52$.
*)

Require Export Reals Lra.
Open Scope R_scope.

Theorem amc12_2001_p9 (f : R -> R) :
  (forall x y : R, 0 < x -> 0 < y -> f (x * y) = f x / y) ->
  f 500 = 3 ->
  f 600 = 5 / 2.
Proof.
Admitted.
