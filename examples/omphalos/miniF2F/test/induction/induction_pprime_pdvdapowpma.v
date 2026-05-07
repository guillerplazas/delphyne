(* miniF2F problem: induction_pprime_pdvdapowpma
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $p$ be a prime number and $a$ a positive integer. Show that $p$ divides $a^p -
   a$.

   Informal proof:
   We show the result by induction on $a$. The result is trivial for $a=0$. Let's assume
   it holds for $a \geq 0$. We have
   $$(a+1)^p - (a+1) = \sum_{k=0}^p \binom{p}{k} a^k - (a+1)$$
   Since $p$ is prime, $p$ divides $\binom{p}{k}$ for every $k$ such that $0 < k < p$.
   So there exists an integer $d$ such that $(a+1)^p - (a+1) = a^p + d \times p + 1 - (a
   + 1) = a^p + d \times p - a$
   By the induction hypothesis, $p$ divides $a^p - a$, so $p$ divides $(a+1)^p - (a+1)$,
   and by induction we have that $p$ divides $a^p-a$ for every positive integer $a$.
*)

Require Import Nat.
Require Import ZArith.
Require Import Znumtheory.

Open Scope nat_scope.

Theorem induction_pprime_pdvdapowpma :
  forall (p a : nat),
    0 < a ->
    prime (Z.of_nat p) ->
    Nat.divide p (pow a p - a).

Proof.
Admitted.
