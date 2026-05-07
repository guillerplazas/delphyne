(* miniF2F problem: numbertheory_prmdvsneqnsqmodpeq0
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any prime $p$ and any integer $n$, we have $p \mid n$ if and only if
   $n^2 \equiv 0 \pmod{p}$.

   Informal proof:
   If $p \mid n$, then $p$ divides any multiple of $n$. In particular, $p \mid n \times
   n$ so $n^2 \equiv 0 \pmod{p}$.
   Reciprocally, if $n^2 \equiv 0 \pmod{p}$ then $p | n^2$. The prime factors in the
   prime decomposition of $n$ and $n^2$ are identical, so if $p$ divides $n^2$, it also
   necessarily divides $n$, hence $p \mid n$.
*)

Require Import ZArith.
Require Import Znumtheory.

Theorem numbertheory_prmdvsneqnsqmodpeq0:
  forall (n : Z) (p : positive),
  prime (Z.pos p) -> (Z.divide (Z.pos p) n <-> (n * n) mod (Z.pos p) = 0%Z).

Proof.
Admitted.
