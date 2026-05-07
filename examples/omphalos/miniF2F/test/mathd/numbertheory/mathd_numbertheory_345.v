(* miniF2F problem: mathd_numbertheory_345
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when $2000+2001+2002+2003+2004+2005+2006$ is divided by $7$?
   Show that it is 0.

   Informal proof:
   Since $2000,2001,\ldots,2006$ are $7$ consecutive integers, they include exactly one
   integer from each residue class $\pmod 7$. Therefore, their sum is congruent $\pmod
   7$ to $0+1+2+3+4+5+6=21$. The remainder of this sum $\pmod 7$ is $0$.
*)

Require Import Arith.

Theorem mathd_numbertheory_345 :
  (2000 + 2001 + 2002 + 2003 + 2004 + 2005 + 2006) mod 7 = 0.
Proof.
Admitted.