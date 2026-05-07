(* miniF2F problem: mathd_numbertheory_447
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of the units digits of all the multiples of $3$ between $0$ and $50$?
   Show that it is 78.

   Informal proof:
   We start by computing the sum of the units digits of all multiples of $3$ between $0$
   and $30$. Excluding $0$, every possible digit appears exactly once as a unit digit of
   a multiple of $3$: the set of multiples of $3$ between $0$ and $30$ consists of the
   numbers $0,3,6,9,12,15,18,21,24,27,30$. Thus, the sum of their units digits is equal
   to $$1+2+3+4+5+6+7+8+9 = \frac{9 \cdot 10}{2} = 45.$$ We must sum the units digits of
   the multiples of $3$ between $31$ and $50$. The relevant multiples of $3$ are 
   $33,36,39,42,45,48$, and the sum of their units digits is $3+6+9+2+5+8 = 33$. Thus,
   the answer is $45 + 33 = 78$.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.PeanoNat.
Import ListNotations.



Theorem mathd_numbertheory_447 :
  fold_right plus 0
    (map (fun k => k mod 10)
         (filter (fun x => Nat.eqb (x mod 3) 0)
                 (seq 1 49))) = 78.

Proof.
Admitted.
