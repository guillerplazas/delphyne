(* miniF2F problem: mathd_numbertheory_543
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find the number of distinct positive divisors of $(30)^4$ excluding 1 and $(30)^4$.
   Show that it is 123.

   Informal proof:
   $$ (30^4) = (2^1 \cdot 3^1 \cdot 5^1)^4 = 2^4 \cdot 3^4 \cdot 5^4 $$Since $t(30^4) =
   (4+1)^3 = 125$, taking out 1 and $(30^4)$ leaves $125 - 2 = 123$ positive divisors.
*)

Require Import Nat.
Require Import List.

Fixpoint divisors_aux (n k: nat) : list nat :=
  match k with
  | 0 => nil
  | S k' => if (n mod k =? 0) 
            then k :: (divisors_aux n k')
            else divisors_aux n k'
  end.

Definition divisors (n: nat) := divisors_aux n n.

Theorem mathd_numbertheory_543:
  (length (divisors (30 ^ 4))) - 2 = 123.

Proof.
Admitted.
