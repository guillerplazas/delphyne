(* miniF2F problem: amc12a_2016_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The remainder can be defined for all real numbers $x$ and $y$ with $y \neq 0$ by
   $\text{rem} (x ,y)=x-y\left \lfloor \frac{x}{y} \right \rfloor$where $\left \lfloor
   \tfrac{x}{y} \right \rfloor$ denotes the greatest integer less than or equal to
   $\tfrac{x}{y}$. What is the value of $\text{rem} (\tfrac{3}{8}, -\tfrac{2}{5} )$?

   $\textbf{(A) } -\frac{3}{8} \qquad \textbf{(B) } -\frac{1}{40} \qquad \textbf{(C) } 0
   \qquad \textbf{(D) } \frac{3}{8} \qquad \textbf{(E) } \frac{31}{40}$ Show that it is
   \textbf{(B) } -\frac{1}{40}.

   Informal proof:
   The value, by definition, is $\begin{align*}
   \text{rem}\left(\frac{3}{8},-\frac{2}{5}\right)
   &=
   \frac{3}{8}-\left(-\frac{2}{5}\right)\left\lfloor\frac{\frac{3}{8}}{-\frac{2}{5}}\right\rfloor
   \\
   &=
   \frac{3}{8}-\left(-\frac{2}{5}\right)\left\lfloor\frac{3}{8}\times\frac{-5}{2}\right\rfloor
   \\
   &= \frac{3}{8}-\left(-\frac{2}{5}\right)\left\lfloor\frac{-15}{16}\right\rfloor\\
   &= \frac{3}{8}-\left(-\frac{2}{5}\right)\left(-1\right)\\
   &= \frac{3}{8}-\frac{2}{5}\\
   &= \textbf{(B) } -\frac{1}{40}.
   \end{align*}$
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.


Parameter Rfloor : R -> Z.
Axiom Rfloor_spec : forall x : R,
  IZR (Rfloor x) <= x < IZR (Rfloor x) + 1.



Theorem amc12a_2016_p3:
  forall (f : R -> R -> R),
    (forall (x y : R), y <> 0 -> f x y = x - y * IZR (Rfloor (x / y))) ->
    f (3 / 8) (-(2 / 5)) = -(1 / 40).

Proof.
Admitted.
