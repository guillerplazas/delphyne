(* miniF2F problem: amc12_2000_p15
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f$ be a [[function]] for which $f\left(\dfrac{x}{3}\right) = x^2 + x + 1$. Find
   the sum of all values of $z$ for which $f(3z) = 7$.

   $\text {(A)}\ -1/3 \qquad \text {(B)}\ -1/9 \qquad \text {(C)}\ 0 \qquad \text {(D)}\
   5/9 \qquad \text {(E)}\ 5/3$ Show that it is \textbf{(B) }-\frac19.

   Informal proof:
   Let $y = \frac{x}{3}$; then $f(y) = (3y)^2 + 3y + 1 = 9y^2 + 3y+1$. Thus
   $f(3z)-7=81z^2+9z-6=3(9z-2)(3z+1)=0$, and $z = -\frac{1}{3}, \frac{2}{9}$. These sum
   up to $\textbf{(B) }-\frac19$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import List.

Open Scope C_scope.

Theorem amc12_2000_p15 :
  forall (f : C -> C),
  (forall x : C, f (x / 3) = x^2 + x + 1) ->
  (exists l : list C, NoDup l /\
    (forall z : C, f (3*z) = 7 <-> In z l) /\
    fold_left Cplus l 0 = -1/9).
Proof.
Admitted.
