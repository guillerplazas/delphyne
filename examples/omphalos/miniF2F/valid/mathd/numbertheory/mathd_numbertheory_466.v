(* miniF2F problem: mathd_numbertheory_466
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when $1 + 2 + 3 + 4 + \dots + 9 + 10$ is divided by 9? Show
   that it is 1.

   Informal proof:
   Looking at our sum, we can see that the numbers $1$ through $8$ can be paired off to
   form $9,$ so we may eliminate them. That is, $1 + 8 = 2 + 7 = 3 + 6 = 4 + 5 = 9.$
   Therefore, the only remaining terms are $9$ and $10,$ and $9$ is obviously also
   divisible by $9,$ hence we only need to find the remainder of $10$ when divided by
   $9,$ which is $1.$
*)

Require Import Arith.

Theorem mathd_numbertheory_466 : 
  (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10) mod 9 = 1.
Proof.
Admitted.