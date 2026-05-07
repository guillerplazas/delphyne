(* miniF2F problem: mathd_numbertheory_353
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $S = 2010 + 2011 + \cdots + 4018$. Compute the residue of $S$, modulo 2009. Show
   that it is 0.

   Informal proof:
   Modulo 2009, $S \equiv 1 + 2 + \cdots + 2008 + 0$. Now, the right-hand side is simply
   the sum of the integers from 1 to 2008, which is $\frac{2008 \cdot 2009}{2} = 1004
   \cdot 2009$, so $S \equiv 1004 \cdot 2009 \equiv 1004 \cdot 0 \equiv 0$ modulo 2009.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Lists.List.
Import List.ListNotations.



Theorem mathd_numbertheory_353 :
  forall (s : nat),
    s = fold_left plus (seq 2010 (4018 - 2010 + 1)) 0 ->
    s mod 2009 = 0.

Proof.
Admitted.
