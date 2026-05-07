(* miniF2F problem: mathd_numbertheory_341
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the sum of the final three digits of the integer representation of $5^{100}$?
   Show that it is 13.

   Informal proof:
   Let's find the cycle of the final three digits of $5^n$, starting with $n=3$ : $125,
   625, 125, 625,\ldots$ . The cycle of the final three digits of $5^{n}$ is 2 numbers
   long: 125, 625. Thus, to find the final three digits of $5^n$ for any positive
   $n\ge3$, we must find the remainder, $R$, when $n$ is divided by 2 ($R=1$ corresponds
   to 125, and $R=0$ corresponds to 625). Since $100\div2=50$ without remainder, the
   final three digits of $5^{100}$ are 625. Their sum is $6+2+5=13$.
*)

Require Import Nat.

Theorem mathd_numbertheory_341 :
  forall a b c : nat,
  (a <= 9) -> (b <= 9) -> (c <= 9) ->
  (5^100 mod 1000 = 100*a + 10*b + c) ->
  a + b + c = 13.
Proof.
Admitted.