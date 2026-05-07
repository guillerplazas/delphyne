(* miniF2F problem: amc12b_2002_p11
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The positive integers $A, B, A-B, $ and $A+B$ are all prime numbers. The sum of these
   four primes is

   $\mathrm{(A)}\ \mathrm{even}
   \qquad\mathrm{(B)}\ \mathrm{divisible\ by\ }3
   \qquad\mathrm{(C)}\ \mathrm{divisible\ by\ }5
   \qquad\mathrm{(D)}\ \mathrm{divisible\ by\ }7
   \qquad\mathrm{(E)}\ \mathrm{prime}$ Show that it is \mathrm{(E)}\ \text{prime}.

   Informal proof:
   Since $A-B$ and $A+B$ must have the same [[parity]], and since there is only one even
   prime number, it follows that $A-B$ and $A+B$ are both odd. Thus one of $A, B$ is odd
   and the other even. Since $A+B > A > A-B > 2$, it follows that $A$ (as a prime
   greater than $2$) is odd. Thus $B = 2$, and $A-2, A, A+2$ are consecutive odd primes.
   At least one of $A-2, A, A+2$ is divisible by $3$, from which it follows that $A-2 =
   3$ and $A = 5$. The sum of these numbers is thus $17$, a prime, so the answer is
   $\mathrm{(E)}\ \text{prime}$.
*)

Require Import ZArith.
Require Import Znumtheory.

Theorem amc12b_2002_p11:
  forall (a b : Z),
    prime a ->
    prime b ->
    prime (a + b) ->
    prime (a - b) ->
    prime (a + b + (a - b + (a + b))).

Proof.
Admitted.
