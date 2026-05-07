(* miniF2F problem: mathd_numbertheory_320
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What integer $n$ satisfies $0\le n<{101}$ and $$123456\equiv n\pmod {101}~?$$ Show
   that it is 34.

   Informal proof:
   Notice that $100\equiv-1\pmod{101}$.  Therefore 
   \[120000\equiv-1200\equiv12\pmod{101}.\]Likewise 
   \[3400\equiv-34\pmod{101}.\]Combining these lets us write  \[123456\equiv
   12-34+56\pmod{101}\]or  \[123456\equiv34\pmod{101}.\]
*)

Require Import ZArith.
Require Import Lia.

Open Scope Z_scope.

Theorem mathd_numbertheory_320 :
  forall (n : Z),
    (0 <= n < 101)%Z ->
    (exists k : Z, 123456 - n = k * 101)%Z ->
    n = 34.

Proof.
Admitted.
