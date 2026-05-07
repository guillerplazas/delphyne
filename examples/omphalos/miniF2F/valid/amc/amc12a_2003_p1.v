(* miniF2F problem: amc12a_2003_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the difference between the sum of the first $2003$ even counting numbers and
   the sum of the first $2003$ odd counting numbers? 

   $ \mathrm{(A) \ } 0\qquad \mathrm{(B) \ } 1\qquad \mathrm{(C) \ } 2\qquad \mathrm{(D)
   \ } 2003\qquad \mathrm{(E) \ } 4006 $ Show that it is \mathrm{(D)}\ 2003.

   Informal proof:
   The first $2003$ even counting numbers are $2,4,6,...,4006$. 

   The first $2003$ odd counting numbers are $1,3,5,...,4005$. 

   Thus, the problem is asking for the value of $(2+4+6+...+4006)-(1+3+5+...+4005)$. 

   $(2+4+6+...+4006)-(1+3+5+...+4005) = (2-1)+(4-3)+(6-5)+...+(4006-4005) $ 

   $= 1+1+1+...+1 = \mathrm{(D)}\ 2003$
*)

Require Import Coq.Lists.List.
Import ListNotations.

Fixpoint sum_f (f : nat -> nat) (n : nat) : nat :=
  match n with
  | 0 => 0
  | S n' => sum_f f n' + f n'
  end.

Theorem amc12a_2003_p1:
    sum_f (fun n => 2*n+2) 2003 - sum_f (fun n => 2*n+1) 2003 = 2003.
Proof.
Admitted.
