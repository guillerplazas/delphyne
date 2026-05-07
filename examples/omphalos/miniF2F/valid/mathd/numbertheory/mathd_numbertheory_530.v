(* miniF2F problem: mathd_numbertheory_530
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $n$ and $k$ are positive integers such that $5<\frac nk<6$, then what is the
   smallest possible value of $\frac{\mathop{\text{lcm}}[n,k]}{\gcd(n,k)}$? Show that it
   is 22.

   Informal proof:
   We can consider both $n$ and $k$ as multiples of their greatest common divisor:
   \begin{align*}
   n &= n'\cdot\gcd(n,k), \\
   k &= k'\cdot\gcd(n,k),
   \end{align*}where $n'$ and $k'$ are relatively prime integers. Then
   $\mathop{\text{lcm}}[n,k] = \frac{n\cdot k}{\gcd(n,k)} = n'\cdot k'\cdot\gcd(n,k)$,
   so $$\frac{\mathop{\text{lcm}}[n,k]}{\gcd(n,k)} = n'k'.$$We have $\frac{n'}{k'} =
   \frac nk$. So, we wish to minimize $n'k'$ under the constraint that
   $5<\frac{n'}{k'}<6$. That is, we wish to find the smallest possible product of the
   numerator and denominator of a fraction whose value is between 5 and 6. Clearly the
   denominator $k'$ is at least $2$, and the numerator $n'$ is at least $5(2)+1=11$, so
   the smallest possible value for $n'k'$ is $(11)(2)=22$.

   Note that this result, $\frac{\mathop{\text{lcm}}[n,k]}{\gcd(n,k)}=22$, can be
   achieved by the example $n=11,k=2$.
*)

Require Import Reals.
Require Import Arith.
Require Import Nat.
Require Import ZArith.

Open Scope R_scope.

Theorem mathd_numbertheory_530 :
  forall (n k : nat),
  (0 < n)%nat ->
  (0 < k)%nat ->
  (IZR (Z_of_nat n) / IZR (Z_of_nat k) < 6)%R ->
  (5 < IZR (Z_of_nat n) / IZR (Z_of_nat k))%R ->
  (22 <= Nat.div (Nat.lcm n k) (Nat.gcd n k))%nat.

Proof.
Admitted.
