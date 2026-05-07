(* miniF2F problem: mathd_numbertheory_552
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = 12x+7$ and $g(x) = 5x+2$ whenever $x$ is a positive integer. Define
   $h(x)$ to be the greatest common divisor of $f(x)$ and $g(x)$. What is the sum of all
   possible values of $h(x)$? Show that it is 12.

   Informal proof:
   Use the Euclidean algorithm on $f(x)$ and $g(x)$. \begin{align*}
   h(x) &= \gcd(f(x), g(x)) \\
   &= \gcd(12x+7, 5x+2) \\
   &= \gcd(5x+2, (12x+7)-2(5x+2)) \\
   &= \gcd(5x+2, 2x + 3) \\
   &= \gcd(2x+3, (5x+2)-2(2x+3)) \\
   &= \gcd(2x+3, x - 4) \\
   &= \gcd(x-4, (2x+3)-2(x-4)) \\
   &= \gcd(x-4, 11)
   \end{align*}From applying the Euclidean algorithm, we have that the greatest common
   divisor of $f(x)$ and $g(x)$ is 11 if and only if $x-4$ is a multiple of 11. For
   example, note that $f(4) = 55$ and $g(4) = 22$, and the greatest common divisor of 55
   and 22 turns out to be 11. If $x-4$ is not a multiple of 11, then the greatest common
   divisor of $f(x)$ and $g(x)$ must be one, since 11 is prime and therefore has no
   other factors. It follows that $h(x)$ can take on two distinct values; 1 and 11. The
   sum of all possible values of $h(x)$ is therefore $1 + 11 = 12$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Lists.List.
Require Import Coq.Init.Nat.
Require Import Coq.Bool.Bool.

Import ListNotations.

Theorem mathd_numbertheory_552 :
  forall (f g h : nat -> nat),
    (forall x, x > 0 -> f x = 12 * x + 7) ->
    (forall x, x > 0 -> g x = 5 * x + 2) ->
    (forall x, x > 0 -> h x = Nat.gcd (f x) (g x)) ->
    
    exists l : list nat,
      NoDup l /\
      (forall y, In y l <-> exists x, x > 0 /\ h x = y) /\
      List.fold_left Nat.add l 0 = 12.

Proof.
Admitted.
