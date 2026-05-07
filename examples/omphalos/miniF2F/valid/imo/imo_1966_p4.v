(* miniF2F problem: imo_1966_p4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Prove that for every natural number $n$, and for every real number $x \neq
   \frac{k\pi}{2^t}$ ($t=0,1, \dots, n$; $k$ any integer)
   $ \frac{1}{\sin{2x}}+\frac{1}{\sin{4x}}+\dots+\frac{1}{\sin{2^nx}}=\cot{x}-\cot{2^nx}
   $

   Informal proof:
   Assume that
   $\frac{1}{\sin{2x}}+\frac{1}{\sin{4x}}+\dots+\frac{1}{\sin{2^{n}x}}=\cot{x}-\cot{2^{n}x}$
   is true, then we use $n=1$ and get $\cot x - \cot 2x = \frac {1}{\sin 2x}$.

   First, we prove $\cot x - \cot 2x = \frac {1}{\sin 2x}$

   LHS=$\frac{\cos x}{\sin x}-\frac{\cos 2x}{\sin 2x}$

   $= \frac{2\cos^2 x}{2\cos x \sin x}-\frac{2\cos^2 x -1}{\sin 2x}$

   $=\frac{2\cos^2 x}{\sin 2x}-\frac{2\cos^2 x -1}{\sin 2x}$

   $=\frac {1}{\sin 2x}$

   Using the above formula, we can rewrite the original series as 

   $\cot x - \cot 2x + \cot 2x - \cot 4x + \cot 4x \cdot \cdot \cdot + \cot 2^{n-1} x -
   \cot 2^n x $

   Which gives us the desired answer of $\cot x - \cot 2^n x$
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.


Fixpoint sum_1_to_n (f : nat -> R) (n : nat) : R :=
  match n with
  | O => 0
  | S n' => sum_1_to_n f n' + f (S n')
  end.

Theorem imo_1966_p4
  (n : nat)
  (x : R)
  (H0 : forall (k : nat), (0 < k)%nat -> forall (m : Z),
          x <> IZR m * PI / INR (2 ^ k))
  (H1 : (0 < n)%nat) :
  sum_1_to_n (fun k => 1 / sin (INR (2 ^ k) * x)) n
  = 1 / tan x - 1 / tan (INR (2 ^ n) * x).

Proof.
Admitted.
