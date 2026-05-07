(* miniF2F problem: mathd_numbertheory_198
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the tens digit of $5^{2005}$? Show that it is 2.

   Informal proof:
   Note that for $n\geq 2$, the last two digits of $5^n$ are 25.  To prove this, note
   that $5^2\equiv 25 \pmod{100}$, and whenever $5^{n-1}\equiv 25\pmod{100}$, we also
   have $5^n=5\cdot 5^{n-1}\equiv 5\cdot 25 \equiv 125 \equiv 25 \pmod{100}$. Thus the
   tens digit of $5^{2005}$ is $2$.
*)

Require Import ZArith.

Open Scope Z_scope.

Theorem mathd_numbertheory_198 :
  (5 ^ 2005) mod 100 = 25.
Proof.
Admitted.