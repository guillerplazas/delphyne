(* miniF2F problem: mathd_numbertheory_427
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $A$ is the sum of the positive divisors of $500$, what is the sum of the distinct
   prime divisors of $A$? Show that it is 25.

   Informal proof:
   First, we find $A$. The prime factorization of $500$ is $2^2 \cdot 5^3$. Therefore, 
   $$A=(1+2+2^2)(1+5+5^2+5^3)=(7)(156).$$To see why $(1+2+2^2)(1+5+5^2+5^3)$ equals the
   sum of the divisors of 500, note that if you distribute (without simplifying), you
   get 12 terms, with each divisor of $2^2\cdot 5^3$ appearing exactly once.

   Now we prime factorize $7 \cdot 156 = 7 \cdot 2^2 \cdot 3 \cdot 13$. The sum of the
   prime divisors of $A$ is $2+3+7+13=25$.
*)

Require Import Nat.
Require Import List.
Require Import Arith.
Require Import List.
Import ListNotations.


Definition get_divisors (n : nat) :=
  filter (fun k => Nat.eqb (n mod k) 0) (seq 1 (S n)).


Definition sum_list := fold_right plus 0.


Definition is_prime (p : nat) :=
  match p with
  | 0 | 1 => false
  | n => forallb (fun d => negb (Nat.eqb (n mod d) 0)) (seq 2 (n - 2))
  end.

Theorem mathd_numbertheory_427 :
  forall (a : nat),
  a = sum_list (get_divisors 500) ->
  sum_list (filter (fun k => andb (is_prime k) (Nat.eqb (a mod k) 0)) (seq 1 (S a))) = 25.

Proof.
Admitted.
