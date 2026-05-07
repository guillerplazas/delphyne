(* miniF2F problem: amc12a_2008_p4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Which of the following is equal to the [[product]]
   $\frac{8}{4}\cdot\frac{12}{8}\cdot\frac{16}{12}\cdot\cdots\cdot\frac{4n+4}{4n}\cdot\cdots\cdot\frac{2008}{2004}?$

   $\textbf{(A)}\ 251\qquad\textbf{(B)}\ 502\qquad\textbf{(C)}\ 1004\qquad\textbf{(D)}\
   2008\qquad\textbf{(E)}\ 4016$ Show that it is \textbf{(B)}.

   Informal proof:
   $\frac {8}{4}\cdot\frac {12}{8}\cdot\frac {16}{12}\cdots\frac {4n + 4}{4n}\cdots\frac
   {2008}{2004} = \frac {1}{4}\cdot\left(\frac {8}{8}\cdot\frac {12}{12}\cdots\frac
   {4n}{4n}\cdots\frac {2004}{2004}\right)\cdot 2008 = \frac{2008}{4} =$ $502
   \Rightarrow B$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.


Fixpoint Rprod (n : nat) (f : nat -> R) : R :=
  match n with
  | 0 => 1
  | S n' => Rprod n' f * f n
  end.



Theorem amc12a_2008_p4:
  Rprod 501 (fun k => (4 * INR k + 4) / (4 * INR k)) = 502.

Proof.
Admitted.
