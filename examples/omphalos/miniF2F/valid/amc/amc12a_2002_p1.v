(* miniF2F problem: amc12a_2002_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Compute the sum of all the roots of
   $(2x+3)(x-4)+(2x+3)(x-6)=0 $

   $ \textbf{(A) } \frac{7}{2}\qquad \textbf{(B) } 4\qquad \textbf{(C) } 5\qquad
   \textbf{(D) } 7\qquad \textbf{(E) } 13 $ Show that it is \textbf{(A) }7/2.

   Informal proof:
   We expand to get $2x^2-8x+3x-12+2x^2-12x+3x-18=0$ which is $4x^2-14x-30=0$ after
   combining like terms. Using the quadratic part of [[Vieta's Formulas]], we find the
   sum of the roots is $\frac{14}4 = \textbf{(A) }7/2$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import List.

Open Scope C_scope.

Theorem amc12a_2002_p1 :
  forall (f : C -> C) (roots : list C),
    (forall x, f x = (2 * x + 3) * (x - 4) + (2 * x + 3) * (x - 6)) ->
    NoDup roots ->
    (forall x, In x roots <-> f x = 0) ->
    fold_left (fun acc x => acc + x) roots 0 = 7/2.

Proof.
Admitted.
