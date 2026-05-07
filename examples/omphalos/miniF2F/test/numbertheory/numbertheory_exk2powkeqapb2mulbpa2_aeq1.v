(* miniF2F problem: numbertheory_exk2powkeqapb2mulbpa2_aeq1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a$ and $b$ are positive integers and there exists a positive integer $k$ such
   that $2^k = (a + b^2) (b + a^2)$, then show that $a = 1$.

   Informal proof:
   As $a \geq 1$ and $b \geq 1$, $2^k = (a + b^2)(b + a^2) \geq 4$, then $k \geq 2$.
   Since $2^k = (a + b^2)(b + a^2)$, there exists $m \geq 1$ and $n \geq 1$ such that
   $2^m=a+b^2$ and $2^n=a^2+b$. Without loss of generality, we can assume that $b \geq
   a$ so that $m \geq n$ and that there exists $p \geq 0$ such that $m = n + p$.

   We have that $2^m - 2^n = 2^n (2^p - 1) = (a+b^2)-(a^2+b) =
   (b-a)(b+a)+(a-b)=(b-a)(b+a-1)$.
   $a$ and $b$ must have the same parity, otherwise $2$ does not divide $a+b^2$. So
   $b+a-1$ is odd and $2^n \mid b-a$. As a result, there exists $d$ such that
   $b=a+(2^n)d$.
   But $2^n=a^2+b=a^2+a+(2^n)d$, and $a>0$ so necessarily $d=0$ and $a=b$. Also,
   $2^n=a(a+1)$, which is only possible if $a=1$. So $a=b=1$.
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Arith.Arith.
Require Import Coq.Reals.Reals.

Theorem numbertheory_exk2powkeqapb2mulbpa2_aeq1 :
  forall (a b : nat), (0 < a) -> (0 < b) ->
  (exists k : nat, (k > 0) /\ (2 ^ k = (a + b ^ 2) * (b + a ^ 2))) ->
  a = 1.
Proof.
Admitted.