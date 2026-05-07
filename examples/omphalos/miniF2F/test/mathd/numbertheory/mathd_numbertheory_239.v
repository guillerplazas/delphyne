(* miniF2F problem: mathd_numbertheory_239
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Determine the modulo 4 remainder of the following sum: $$ 1 + 2 + 3 + 4 + 5 + 6 + 7 +
   8 + 9 + 10 + 11 + 12. $$ Show that it is 2.

   Informal proof:
   Grouping residues helps make some series computations easier:  \begin{align*}
   1 + 2 + 3 + 0 + 1 + 2& + 3 + 0 + 1 + 2 + 3 + 0\\&\equiv 3(1 + 2 + 3 + 0) \\
   &\equiv 18\\
   & \equiv 2 \pmod{4}.
   \end{align*}
*)

From Coq Require Import Arith List.
Import List.ListNotations.

Theorem mathd_numbertheory_239 :
  list_sum (seq 1 12) mod 4 = 2.
Proof.
Admitted.
