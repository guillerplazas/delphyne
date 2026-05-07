(* miniF2F problem: mathd_numbertheory_709
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $n$ is a positive integer such that $2n$ has 28 positive divisors and $3n$ has 30
   positive divisors, then how many positive divisors does $6n$ have? Show that it is
   35.

   Informal proof:
   Let $\, 2^{e_1} 3^{e_2} 5^{e_3} \cdots \,$ be the prime factorization of $\, n$. 
   Then the  number of positive divisors of $\, n \,$ is $\, (e_1 + 1)(e_2 + 1)(e_3 + 1)
   \cdots \; $. In view of the given information, we have \[
   28 = (e_1 + 2)(e_2 + 1)P
   \]and \[
   30 = (e_1 + 1)(e_2 + 2)P,
   \]where $\, P = (e_3 + 1)(e_4 + 1) \cdots \; $. Subtracting the first equation from
   the second, we obtain $\, 2 = (e_1 - e_2)P,
   \,$ so either $\, e_1 - e_2 = 1 \,$ and $\, P = 2, \,$ or $\, e_1
   - e_2 = 2 \,$ and $\, P = 1$.  The first case yields $\, 14 = (e_1
   + 2)e_1 \,$ and  $\, (e_1 + 1)^2 = 15$; since $\, e_1 \,$ is a nonnegative integer,
   this is impossible. In the second case, $\,
   e_2 = e_1 - 2 \,$ and $\, 30 = (e_1 + 1)e_1, \,$ from which we find $\, e_1 = 5 \,$
   and $\, e_2 = 3$.  Thus $\, n = 2^5 3^3, \,$ so $\, 6n = 2^6 3^4 \,$ has $\,
   (6+1)(4+1) = 35 \,$ positive divisors.
*)

Require Import Coq.Init.Nat.
Require Import Coq.Lists.List.
Require Import Coq.Arith.EqNat.
Require Import Coq.Arith.PeanoNat.
Import ListNotations.

Fixpoint divisors (n : nat) : list nat :=
  if n =? 0 then []
  else filter (fun d => Nat.modulo n d =? 0) (seq 1 n).

Theorem mathd_numbertheory_709
  (n : nat)
  (h₀ : n > 0)
  (h₁ : length (divisors (2 * n)) = 28)
  (h₂ : length (divisors (3 * n)) = 30) :
  length (divisors (6 * n)) = 35.

Proof.
Admitted.
