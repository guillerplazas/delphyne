(* miniF2F problem: mathd_numbertheory_237
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the modulo $6$ remainder of the sum $1+2+3+4+\dots+98+99+100?$ Show that it
   is 4.

   Informal proof:
   Instead of adding up the sum and finding the residue, we can find the residue of each
   number to make computation easier.

   Each group of 6 numbers would have the sum of residues $1+2+3+4+5+0 \equiv 15 \equiv
   3 \pmod6$.

   There are $\left\lfloor\frac{100}{6}\right\rfloor=16$ sets of $6$ numbers. This
   leaves the numbers $97,98,99,$ and $100$, which have the residues $1,2,3,$ and $4$.
   Adding together all the residues, we have $3 \cdot 16 + 1+2+3+4 \equiv 58 \equiv 4
   \pmod6$.
*)

Require Import Coq.Lists.List.
Require Import Coq.Arith.Arith.
Import ListNotations.

Open Scope nat_scope.



Theorem mathd_numbertheory_237:
  Nat.modulo (fold_left plus (seq 0 101) 0) 6 = 4.

Proof.
Admitted.
