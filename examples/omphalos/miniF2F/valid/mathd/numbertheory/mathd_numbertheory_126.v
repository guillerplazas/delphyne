(* miniF2F problem: mathd_numbertheory_126
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The greatest common divisor of two integers is $(x+3)$ and their least common
   multiple is $x(x+3)$, where $x$ is a positive integer. If one of the integers is 40,
   what is the smallest possible value of the other one? Show that it is 8.

   Informal proof:
   We know that $\gcd(m,n) \cdot \mathop{\text{lcm}}[m,n] = mn$ for all positive
   integers $m$ and $n$.  Hence, in this case, the other number is \[\frac{(x + 3) \cdot
   x(x + 3)}{40} = \frac{x(x + 3)^2}{40}.\] To minimize this number, we minimize $x$.

   This expression is not an integer for $x =$ 1, 2, 3, or 4, but when $x = 5$, this
   expression is $5 \cdot 8^2/40 = 8$.

   Note that that the greatest common divisor of 8 and 40 is 8, and $x + 3 = 5 + 3 = 8$.
   The least common multiple is 40, and $x(x + 3) = 5 \cdot (5 + 3) = 40$, so $x = 5$ is
   a possible value.  Therefore, the smallest possible value for the other number is
   $8$.
*)

Require Import PeanoNat.

Theorem mathd_numbertheory_126:
  forall (x a : nat),
  (0 < x) -> (0 < a) ->
  (Nat.gcd a 40 = x + 3) ->
  (Nat.lcm a 40 = x * (x + 3)) ->
  (forall b : nat, (0 < b) -> (Nat.gcd b 40 = x + 3 /\ Nat.lcm b 40 = x * (x + 3) -> a <= b)) ->
  a = 8.
Proof.
Admitted.
