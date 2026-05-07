(* miniF2F problem: mathd_numbertheory_582
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $n$ is a multiple of three, what is the remainder when $(n + 4) + (n + 6) + (n +
   8)$ is divided by $9$? Show that it is 0.

   Informal proof:
   We see that $(n + 4) + (n + 6) + (n + 8) = 3n + 18.$ We can see that this must be a
   multiple of $9,$ since $18$ is a multiple of $9$ and $3n$ is as well, since we are
   given that $n$ is a multiple of $3.$ Therefore, our answer is $0.$
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_582:
  forall n : nat,
  (0 < n) -> (exists k, n = 3 * k) ->
  (((n + 4) + (n + 6) + (n + 8)) mod 9 = 0).
Proof.
Admitted.