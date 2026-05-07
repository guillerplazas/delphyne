(* miniF2F problem: numbertheory_notequiv2i2jasqbsqdiv8
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be two integer numbers. Show that the following statement is false:
   $a$ and $b$ are both even iff $8 \mid a^2 + b^2$.

   Informal proof:
   We attempt the proof by contradiction: assuming the equivalence holds.
   Instantiating $a=2$ and $b=0$, we can see $a^2+b^2=4$ which is not divisible by $8$.
   Hence the equivalence cannot hold.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem numbertheory_notequiv2i2jasqbsqdiv8:
  ~ (forall a b : Z, 
    (exists i j : Z, a = 2 * i /\ b = 2 * j) <-> 
    (exists k : Z, a ^ 2 + b ^ 2 = 8 * k)).
Proof.
Admitted.