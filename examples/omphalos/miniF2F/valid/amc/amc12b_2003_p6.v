(* miniF2F problem: amc12b_2003_p6
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The second and fourth terms of a geometric sequence are $2$ and $6$. Which of the
   following is a possible first term?

   $\textbf{(A) } -\sqrt{3}  \qquad\textbf{(B) } -\frac{2\sqrt{3}}{3} \qquad\textbf{(C)
   } -\frac{\sqrt{3}}{3} \qquad\textbf{(D) } \sqrt{3} \qquad\textbf{(E) } 3$ Show that
   it is \textbf{(B)}\ -\frac{2\sqrt{3}}{3}.

   Informal proof:
   Let the first term be $ a $ and the common ratio be $ r $. Therefore, 

   $ar=2\ \ (1) \qquad \text{and} \qquad ar^3=6\ \ (2)$

   Dividing $(2)$ by $(1)$ eliminates the $ a $, yielding $ r^2=3 $, so $ r=\pm\sqrt{3}
   $.

   Now, since $ ar=2 $, $ a=\frac{2}{r} $, so $
   a=\frac{2}{\pm\sqrt{3}}=\pm\frac{2\sqrt{3}}{3} $.

   We therefore see that $ \textbf{(B)}\ -\frac{2\sqrt{3}}{3} $ is a possible first
   term.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2003_p6 :
  forall (a r : R) (u : nat -> R),
  (forall k : nat, u k = a * pow r k) ->
  u 1%nat = 2 ->
  u 3%nat = 6 ->
  u 0%nat = 2/sqrt(3) \/ u 0%nat = -(2/sqrt(3)).

Proof.
Admitted.
