(* miniF2F problem: induction_seq_mul2pnp1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $u_n$ a sequence defined by $u_0 = 0$ and $\forall n \geq 0, u_{n+1} = 2 u_n + (n
   + 1)$. Show that $\forall n \geq 0, u(n) = 2^{n+1} - (n+2)$.

   Informal proof:
   The property is true for $n=0$, since $2^{0+1}-(0+2)=0$.
   By induction, assuming the property holds for $n\geq 0$, we have
   $u_{n+1}=2u_n+(n+1)=2(2^{n+1}-(n+2))+n+1=2^{n+1+1}-(n+1+2)$, which shows the property
   at $n+1$.
*)

Require Import Nat.

Theorem induction_seq_mul2pnp1 :
  forall n : nat,
  forall u : nat -> nat,
  (u 0 = 0) ->
  (forall n, u (n + 1) = 2 * u n + (n + 1)) ->
  (u n = 2 ^ (n + 1) - (n + 2)).
Proof.
Admitted.