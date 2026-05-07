(* miniF2F problem: mathd_numbertheory_212
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the units digit of $16^{17} \times 17^{18} \times 18^{19}$. Show that it is 8.

   Informal proof:
   We can re-write the given expression as $(16 \times 17 \times 18)^{17} \times 17
   \times 18^2$. First, we find the units digit of $(16 \times 17 \times 18)^{17}$. The
   units digit of $16 \times 17 \times 18$ is that of $6 \times 7 \times 8,$ or that of
   $2 \times 8$, or $6$. When raised to any perfect power, a positive integer ending in
   $6$ will still end in $6$, so $(16 \times 17 \times 18)^{17}$ has a units digit of
   $6$. Now, we need to find the units digit of $6 \times 17 \times 18^2$, or the units
   digit of $2 \times 18^2$, which is $8$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_212 :
  (16^17 * 17^18 * 18^19) mod 10 = 8.
Proof.
Admitted.