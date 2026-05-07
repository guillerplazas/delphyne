(* miniF2F problem: mathd_numbertheory_435
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the smallest positive integer $k$ such that, for every positive integer $n$,
   $6n+k$ is relatively prime to each of $6n+3$, $6n+2$, and $6n+1$. Show that it is 5.

   Informal proof:
   Obviously, we have that $k > 3$, because otherwise two of the integers would be
   identical and not be relatively prime. Start by testing $k=4$. $6n+4$ and $6n+3$ are
   relatively prime because they are consecutive integers, but $6n+4$ and $6n+2$ are
   both even and are therefore not relatively prime. The next candidate to test is
   $k=5$. Firstly, we have that
   \begin{align*}
   \gcd(6n+5, 6n+3) &= \gcd(6n+3, (6n+5)-(6n+3)) \\ &= \gcd(6n+3, 2). 
   \end{align*}Since $6n+3$ is always odd, the two integers $6n+5$ and $6n+3$ are
   relatively prime.
   Secondly,
   \begin{align*}
   \gcd(6n+5, 6n+2) &= \gcd(6n+2, (6n+5)-(6n+2)) \\&= \gcd(6n+2, 3). 
   \end{align*}Note that $6n+3$ is always divisible by 3, so $6n+2$ is never divisible
   by 3. As a result, we have that $6n+5$ and $6n+2$ are relatively prime. Finally,
   \begin{align*}
   \gcd(6n+5, 6n+1) &= \gcd(6n+1, (6n+5)-(6n+1)) \\ &= \gcd(6n+1, 4). 
   \end{align*}Note that $6n+1$ is always odd, so $6n+5$ and $6n+1$ are also relatively
   prime. Therefore, the smallest positive integer $k$ that permits $6n+k$ to be
   relatively prime with each of $6n+3$, $6n+2$, and $6n+1$ is $k = 5$.
*)

Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_435 :
  forall (k : nat),
    0 < k ->
    (forall n : nat, Nat.gcd (6 * n + k) (6 * n + 3) = 1) ->
    (forall n : nat, Nat.gcd (6 * n + k) (6 * n + 2) = 1) ->
    (forall n : nat, Nat.gcd (6 * n + k) (6 * n + 1) = 1) ->
    5 = k \/ 5 < k.
Proof.
Admitted.
