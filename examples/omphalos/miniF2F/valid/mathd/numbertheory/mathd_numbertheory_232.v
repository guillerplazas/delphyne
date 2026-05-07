(* miniF2F problem: mathd_numbertheory_232
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Compute $(3^{-1}+5^{-1})^{-1}\pmod{31}$. Express your answer as an integer from $0$
   to $30$, inclusive. Show that it is 29.

   Informal proof:
   To minimize our work, we may begin by rewriting $3^{-1}+5^{-1}$ in the following way:
   \begin{align*}
   3^{-1}+5^{-1} &\equiv 5\cdot 5^{-1}\cdot 3^{-1} + 3\cdot 3^{-1}\cdot 5^{-1} \\
   &\equiv 5\cdot 15^{-1} + 3\cdot 15^{-1} \\
   &\equiv (5+3)\cdot 15^{-1} \\
   &\equiv 8\cdot 15^{-1},
   \end{align*}where all congruence is modulo $31$. Notice that this process is just
   like finding a common denominator!

   Now we wish to find the inverse of $8\cdot 15^{-1}$. This inverse must be $15\cdot
   8^{-1}$, since $$8\cdot 15^{-1}\cdot 15\cdot 8^{-1} \equiv 8\cdot 1\cdot 8^{-1}
   \equiv 1 \pmod{31}.$$Finally, we note that $8^{-1}\equiv 4\pmod{31}$, since $8\cdot 4
   = 32\equiv 1\pmod{31}$. Therefore, we have \begin{align*}
   (3^{-1}+5^{-1})^{-1} &\equiv 15\cdot 8^{-1} \\
   &\equiv 15\cdot 4 \\
   &\equiv 60 \\
   &\equiv 29 \quad\pmod{31}.
   \end{align*}
*)

Require Import ZArith.
Require Import Ring.
Require Import Znumtheory.

Theorem mathd_numbertheory_232 :
  forall x y z : Z,
  (x * 3) mod 31 = 1 ->
  (y * 5) mod 31 = 1 ->
  (z * (x + y)) mod 31 = 1 ->
  0 <= x < 31 ->
  0 <= y < 31 ->
  0 <= z < 31 ->
  z = 29.
Proof.
Admitted.