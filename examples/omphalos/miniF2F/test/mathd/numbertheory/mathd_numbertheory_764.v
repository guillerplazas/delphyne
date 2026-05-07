(* miniF2F problem: mathd_numbertheory_764
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that $p\ge 7$ is a prime number, evaluate $$1^{-1} \cdot 2^{-1} + 2^{-1} \cdot
   3^{-1} + 3^{-1} \cdot 4^{-1} + \cdots + (p-2)^{-1} \cdot (p-1)^{-1} \pmod{p}.$$ Show
   that it is 2.

   Informal proof:
   As $p$ is a prime number, it follows that the modular inverses of $1,2, \ldots, p-1$
   all exist. We claim that $n^{-1} \cdot (n+1)^{-1} \equiv n^{-1} - (n+1)^{-1}
   \pmod{p}$ for $n \in \{1,2, \ldots, p-2\}$, in analogue with the formula
   $\frac{1}{n(n+1)} = \frac{1}{n} - \frac{1}{n+1}$. Indeed, multiplying both sides of
   the congruence by $n(n+1)$, we find that $$1 \equiv n(n+1) \cdot (n^{-1} -
   (n+1)^{-1}) \equiv (n+1) - n \equiv 1 \pmod{p},$$as desired. Thus,
   \begin{align*}&1^{-1} \cdot 2^{-1} + 2^{-1} \cdot 3^{-1} + 3^{-1} \cdot 4^{-1} +
   \cdots + (p-2)^{-1} \cdot (p-1)^{-1} \\ &\equiv 1^{-1} - 2^{-1} + 2^{-1} - 3^{-1} +
   \cdots - (p-1)^{-1} \pmod{p}.\end{align*}This is a telescoping series, which sums to
   $1^{-1} - (p-1)^{-1} \equiv 1 - (-1)^{-1} \equiv 2 \pmod{p}$, since the modular
   inverse of $-1$ is itself.
*)

Require Import ZArith.
Require Import Znumtheory.
Require Import List.

Open Scope nat_scope.

Definition inverse (n p : nat) := (n ^ (p - 2)) mod p.

Theorem mathd_numbertheory_764 :
  forall (p : nat), 7 <= p ->
  prime (Z.of_nat p) ->
  let l := map (fun k => inverse k p * inverse (k + 1) p) (seq 1 (p - 2)) in
  (fold_left plus l 0) mod p = 2.
Proof.
Admitted.
