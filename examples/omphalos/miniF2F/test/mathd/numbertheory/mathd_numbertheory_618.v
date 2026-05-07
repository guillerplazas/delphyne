(* miniF2F problem: mathd_numbertheory_618
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Euler discovered that the polynomial $p(n) = n^2 - n + 41$ yields prime numbers for
   many small positive integer values of $n$. What is the smallest positive integer $n$
   for which $p(n)$ and $p(n+1)$ share a common factor greater than $1$? Show that it is
   41.

   Informal proof:
   We find that $p(n+1) = (n+1)^2 - (n+1) + 41 = n^2 + 2n + 1 - n - 1 + 41 = n^2 + n +
   41$. By the Euclidean algorithm, \begin{align*} &\text{gcd}\,(p(n+1),p(n)) \\
   &\qquad = \text{gcd}\,(n^2+n+41,n^2 - n+41) \\
   &\qquad = \text{gcd}\,(n^2 + n + 41 - (n^2 - n + 41), n^2 - n + 41) \\
   &\qquad = \text{gcd}\,(2n,n^2-n+41). \end{align*}Since $n^2$ and $n$ have the same
   parity (that is, they will both be even or both be odd), it follows that $n^2 - n +
   41$ is odd. Thus, it suffices to evaluate $\text{gcd}\,(n,n^2 - n + 41) =
   \text{gcd}\,(n,n^2-n+41 - n(n-1)) = \text{gcd}\,(n,41)$. The smallest desired
   positive integer is then $n = 41$.

   In fact, for all integers $n$ from $1$ through $40$, it turns out that $p(n)$ is a
   prime number.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.ZArith.BinInt.

Theorem mathd_numbertheory_618:
  forall n : nat,
  forall p : nat -> nat,
  (forall x, p x = x*x - x + 41) ->
  0 < n ->
  1 < Nat.gcd (p n) (p (S n)) ->
  41 <= n.
Proof.
Admitted.
