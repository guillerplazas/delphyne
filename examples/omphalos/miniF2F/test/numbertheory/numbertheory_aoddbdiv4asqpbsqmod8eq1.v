(* miniF2F problem: numbertheory_aoddbdiv4asqpbsqmod8eq1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ be an odd integer number and $b$ be a natural number such that $4 \mid b$.
   Show that $a^2 + b^2 \equiv 1 \mod 8$.

   Informal proof:
   Since $4 \mid b$, we know that $b \equiv 0 \pmod 8$ or $b \equiv 4 \pmod 8$, hence
   $b^2 \equiv 0^2 \equiv 0 \pmod 8$ or $b^2 \equiv 4^2 \equiv 0 \pmod 8$.
   Because $a$ is odd, we know that $a \pmod 8 \in \{1, 3, 5, 7\}$. Hence $a^2 \pmod 8
   \in \{1^2\pmod 8, 3^2\pmod 8, 5^2\pmod 8, 7^2\pmod 8\} = \{1\}$. 
   Therefore $a^2 + b^2 \equiv 1 + 0 \equiv 1 \pmod 8$.
*)

Require Import ZArith.
Require Import Nat.
Require Import Lia.

Open Scope Z_scope.

Theorem numbertheory_aoddbdiv4asqpbsqmod8eq1 :
  forall (a : Z) (b : nat),
    Z.odd a = true ->
    (exists k : nat, b = 4 * k)%nat ->
    (a * a + Z.of_nat (b * b)) mod 8 = 1.

Proof.
Admitted.
