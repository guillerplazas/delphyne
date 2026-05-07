(* miniF2F problem: numbertheory_nckeqnm1ckpnm1ckm1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integers $n$ and $k$ with $k \leq n$, we have 
   $\binom{n}{k} = \binom{n-1}{k} + \binom{n-1}{k-1}$.

   Informal proof:
   We have $\binom{n-1}{k} + \binom{n-1}{k-1} = \frac{(n-1)!}{k!(n-1-k)!} +
   \frac{(n-1)!}{(k-1)!(n-k)!} = \frac{(n-k) (n-1)!}{k!(n-k)!} + \frac{k
   (n-1)!}{k!(n-k)!}$.
   So $\binom{n-1}{k} + \binom{n-1}{k-1} = \frac{((n-k) + k) (n-1)!}{k!(n-k)!} =
   \frac{n!}{k!(n-k)!} = \binom{n}{k}$.
*)

Require Import Arith.

Definition choose n k :=
  if k <=? n then fact n / (fact k * fact (n - k)) else 0.

Theorem numbertheory_nckeqnm1ckpnm1ckm1 :
  forall (n k : nat),
    0 < k <= n ->
    choose n k = choose (n-1) k + choose (n-1) (k-1).
Proof.
Admitted.
