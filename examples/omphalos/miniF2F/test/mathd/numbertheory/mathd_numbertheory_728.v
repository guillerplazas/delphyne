(* miniF2F problem: mathd_numbertheory_728
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Compute $29^{13} - 5^{13}$ modulo 7. Show that it is 3.

   Informal proof:
   Firstly, note that $29 \equiv 1$ modulo 7, so $29^{13} \equiv 1$ modulo 7. Also, $5
   \equiv (-2)$, so $1 - 5^{13} \equiv 1 + 2^{13}$ modulo 7. Finally, $2^3 \equiv 1$
   modulo 7, so $2^{13} \equiv 2(2^3)^4 \equiv 2 \cdot 1 \equiv 2$. Thus $29^{13} -
   5^{13} \equiv 1+2 \equiv 3$ modulo 7.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_728 : (29^13 - 5^13) mod 7 = 3.
Proof.
Admitted.