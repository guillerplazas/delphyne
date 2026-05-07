(* miniF2F problem: mathd_numbertheory_37
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Compute the least common multiple of $9999$ and $100{,}001$. Show that it is
   90{,}900{,}909.

   Informal proof:
   Recall the identity $\mathop{\text{lcm}}[a,b]\cdot \gcd(a,b)=ab$, which holds for all
   positive integers $a$ and $b$. Thus, $$\mathop{\text{lcm}}[9999,100001] =
   \frac{9999\cdot 100001}{\gcd(9999,100001)},$$so we focus on computing
   $\gcd(9999,100001)$.

   Notice that $100001 = 99990+11 = 10(9999)+11$. Therefore, any common divisor of
   $100001$ and $9999$ must be a divisor of $100001-10\cdot 9999 = 11$. The
   possibilities are $1$ and $11$.

   In fact, $9999=11\cdot 909$, so $11$ is a divisor of $9999$ and $100001$, which gives
   $\gcd(9999,100001) = 11$.

   Therefore, \begin{align*}
   \mathop{\text{lcm}}[9999,100001] &= \frac{9999\cdot 100001}{11} \\
   &= 909\cdot 100001 \\
   &= 909\cdot 100000 + 909 \\
   &= 90{,}900{,}909.
   \end{align*}
*)

Require Import Arith.

Theorem mathd_numbertheory_37 :
  Nat.lcm 9999 100001 = 90900909.
Proof.
Admitted.
