(* miniF2F problem: imo_1967_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $k, m, n$ be natural numbers such that $m+k+1$ is a prime greater than $n+1.$ Let
   $c_s=s(s+1).$ Prove that the product $(c_{m+1}-c_k)(c_{m+2}-c_k)\cdots (c_{m+n}-c_k)$
   is divisible by the product $c_1c_2\cdots c_n$.

   Informal proof:
   We have that $c_1c_2c_3...c_n=n!(n+1)$

   and we have that $c_a-c_b=a^2-b^2+a-b=(a-b)(a+b+1)$

   So we have that
   $(c_{m+1}-c_k)(c_{m+2}-c_k)\ldots(c_{m+n}-c_k)=\frac{(m+n-k)!}{(m-n)!}\frac{(m+n+k+1)!}{(m+k+1)!}$
   We have to show that:

   $\frac{(c_{m+1}-c_k)(c_{m+2}-c_k)\ldots(c_{m+n}-c_k)}{n!(n+1)!}=\frac{(m+n-k)!}{(m-n)!n!}\frac{(m+n+k+1)!}{(m+k)!(n+1)!}
   \frac 1{m+k+1}$ is an integer

   But $\frac{(m+n-k)!}{(m-n)!n!}=\binom {m+n-k}n$ is an integer and
   ${(m+n+k+1)!}{(m+k)!(n+1)!} \frac 1{m+k+1}=\binom {m+n+k+1}{n+1}\frac 1{m+k+1}$ is an
   integer because $m+k+1|m+n+k+1!$ but does not divide neither $n+1!$ nor $m+n!$
   because $m+k+1$ is prime and it is greater than $n+1$ (given in the hypotesis) and
   $m+n$.

   The above solution was posted and copyrighted by Simo_the_Wolf. The original thread
   can be found here: [https://aops.com/community/p392191]
*)

Require Import Nat.
Require Import Arith.


Definition is_prime (p : nat) := 
  p > 1 /\ forall n, 1 < n < p -> ~(exists k, n * k = p).


Fixpoint prod_from_1_to (f : nat -> nat) (n : nat) : nat :=
  match n with
  | 0 => 1
  | S m => (prod_from_1_to f m) * (f (S m))
  end.


Theorem imo_1967_p3 :
  forall (k m n : nat) (c : nat -> nat),
    0 < k /\ 0 < m /\ 0 < n ->
    (forall s, c s = s * (s + 1)) ->
    is_prime (k + m + 1) ->
    n + 1 < k + m + 1 ->
    exists d : nat,
      prod_from_1_to c n * d = prod_from_1_to (fun i => c (m + i) - c k) n.

Proof.
Admitted.
