(* miniF2F problem: mathd_numbertheory_252
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when $7!$ is divided by $23$?

   (Note: $n!$ means ''n factorial'', defined as the product of all integers from $1$ to
   $n$.) Show that it is 3.

   Informal proof:
   $7!$ is defined as $1\cdot 2\cdot 3\cdot 4\cdot 5\cdot 6\cdot 7$.

   Note that $1\cdot 2\cdot 3\cdot 4 = 24 \equiv 1\pmod{23}$. So, $$7! \equiv 1\cdot
   5\cdot 6\cdot 7\pmod{23}.$$Furthermore, we have $1\cdot 5\cdot 6 = 30\equiv 7
   \pmod{23}$, so \begin{align*}
   7! &\equiv 7\cdot 7 \\
   &= 49 \\
   &\equiv 3 \pmod{23}.
   \end{align*}The remainder is $3$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Arith.Factorial.



Theorem mathd_numbertheory_252 :
  (fact 7) mod 23 = 3.

Proof.
Admitted.
