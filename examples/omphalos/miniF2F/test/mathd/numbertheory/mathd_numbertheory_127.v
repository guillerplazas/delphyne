(* miniF2F problem: mathd_numbertheory_127
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the remainder when $1 + 2 + 2^2 + 2^3 + \dots + 2^{100}$ is divided by 7. Show
   that it is 3.

   Informal proof:
   To find the sum, we look at the first few powers of 2 modulo 7: \begin{align*}
   2^0 &\equiv 1, \\
   2^1 &\equiv 2, \\
   2^2 &\equiv 4, \\
   2^3 &\equiv 8 \equiv 1 \pmod{7}
   \end{align*}Since $2^3 \equiv 1 \pmod{7}$, the powers of 2 modulo 7 repeat in cycles
   of 3.  Therefore, \begin{align*}
   &1 + 2 + 2^2 + 2^3 + \dots + 2^{100} \\
   &\quad\equiv 1 + 2 + 4 + 1 + 2 + 4 + \dots + 1 + 2 + 4 + 1 + 2 \\
   &\quad\equiv (1 + 2 + 4) + (1 + 2 + 4) + \dots + (1 + 2 + 4) + 1 + 2 \\
   &\quad\equiv 3 \pmod{7}.
   \end{align*}
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Lists.List.
Import ListNotations.



Theorem mathd_numbertheory_127 :
  (fold_left (fun acc k => acc + 2 ^ k) (seq 0 101) 0) mod 7 = 3.

Proof.
Admitted.
