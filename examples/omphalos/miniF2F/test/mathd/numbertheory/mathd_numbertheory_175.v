(* miniF2F problem: mathd_numbertheory_175
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the units digit of $2^{2010}$? Show that it is 4.

   Informal proof:
   Let's start by finding the units digit of small powers of 2. \begin{align*}
   2^1 &= 2 \\
   2^2 &= 4 \\
   2^3 &= 8 \\
   2^4 &= 16 \\
   2^5 &= 32 \\
   2^6 &= 64 \\
   2^7 &= 128 \\
   2^8 &= 256 \\
   \end{align*}It looks like the units digit repeats every time the exponent is
   increased by 4. The remainder when 2010 is divided by 4 is 2, so $2^{2010}$ has the
   same units digit as $2^2$, which is $4$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_175 :
  (2^2010) mod 10 = 4.
Proof.
Admitted.