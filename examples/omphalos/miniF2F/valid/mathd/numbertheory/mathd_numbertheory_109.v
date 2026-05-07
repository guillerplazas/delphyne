(* miniF2F problem: mathd_numbertheory_109
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the modulo $7$ remainder of the sum $1+3+5+7+9+\dots+195+197+199.$ Show that it
   is 4.

   Informal proof:
   Instead of adding up the sum and finding the residue, we can find the residue of each
   number to make computation easier.

   Each group of 7 numbers would have the sum of residues $1+3+5+0+2+4+6 \equiv 21
   \equiv 0 \pmod7$. Since we only have odd numbers in the sum, every $7$ odd numbers is
   $14$ integers. Because every group has a residue of $7$, we can ignore them.

   There are $\left\lfloor \frac{199}{14}\right\rfloor=14$ sets of $14$ integers, which
   is equivalent to $7$ odd numbers in our sum. This leaves $197$ and $199$, which have
   residues $1+3 \equiv 4 \pmod7$.
*)

Require Import Arith.
Require Import List.
Import ListNotations.

Theorem mathd_numbertheory_109 :
  forall (v : nat -> nat),
    (forall n, v n = 2 * n - 1) ->
    (list_sum (map v (seq 1 100))) mod 7 = 4.
Proof.
Admitted.
