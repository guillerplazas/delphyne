(* miniF2F problem: mathd_numbertheory_521
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The product of two consecutive positive even integers is 288. What is the greater of
   the two integers? Show that it is 18.

   Informal proof:
   First we find the prime factorization of 288 to be $2^5\cdot 3^2$, and we have to
   split these factors among two consecutive even integers. The 3 must be with at least
   one 2 for the integer to be even, meaning one of the factors must be a multiple of
   $6.$ After some playing around, we find that when one factor is 18, that leaves us
   with $2^4=16$. So, our two integers are 16 and 18, with the greater integer being
   $18$.
*)

Require Import Nat.

Theorem mathd_numbertheory_521 :
  forall m n : nat,
    (exists k1, m = 2 * k1) ->  
    (exists k2, n = 2 * k2) ->  
    m - n = 2 ->               
    m * n = 288 ->            
    m = 18.                   

Proof.
Admitted.
