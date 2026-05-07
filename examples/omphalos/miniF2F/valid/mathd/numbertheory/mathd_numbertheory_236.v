(* miniF2F problem: mathd_numbertheory_236
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when $1999^{2000}$ is divided by $5?$ Show that it is 1.

   Informal proof:
   Since any positive integer(expressed in base ten) is some multiple of $5$ plus its
   last digit, its remainder when divided by $5$ can be obtained by knowing its last
   digit.

   Note that $1999^1$ ends in $9,$ $1999^2$ ends in $1,$ $1999^3$ ends in $9,$ $1999^4$
   ends in $1,$ and this alternation of $9$ and $1$ endings continues with all even
   powers ending in $1.$ Therefore, the remainder when $1999^{2000}$ is divided by $5$
   is $1.$
*)

Require Import Nat.

Theorem mathd_numbertheory_236:
  (1999 ^ 2000) mod 5 = 1.
Proof.
Admitted.