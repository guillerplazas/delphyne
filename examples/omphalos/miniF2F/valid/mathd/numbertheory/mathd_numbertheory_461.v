(* miniF2F problem: mathd_numbertheory_461
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $n$ be the number of integers $m$ in the range $1\le m\le 8$ such that
   $\text{gcd}(m,8)=1$. What is the remainder when $3^n$ is divided by $8$? Show that it
   is 1.

   Informal proof:
   The subset of $\{1,2,3,4,5,6,7,8\}$ that contains the integers relatively prime to
   $8$ is $\{1,3,5,7\}$. So $n=4$ and $3^4=9^2\equiv 1^2=1\pmod 8$.
*)

Require Import Nat.
Require Import ZArith.
Require Import List.

Theorem mathd_numbertheory_461 :
  forall n : nat,
  n = length (filter (fun x => Nat.gcd x 8 =? 1) (seq 1 7)) ->
  (Nat.modulo (3^n) 8) = 1.
Proof.
Admitted.