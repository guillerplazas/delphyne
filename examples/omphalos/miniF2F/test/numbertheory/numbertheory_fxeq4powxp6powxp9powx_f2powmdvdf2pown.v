(* miniF2F problem: numbertheory_fxeq4powxp6powxp9powx_f2powmdvdf2pown
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x) = 4^x + 6^x + 9^x$. Show that if $m$ and $n$ are positive integers with $m
   \leq n$, then $f(2^m)$ divides $f(2^n)$.

   Informal proof:
   Since $m \leq n$, we can have $k=n-m$ to be a natural number. Then we can do
   induction on $k$.
   Base case is trivial when $k=0$.
   For the inductive case, we assume that $f(2^m) | f(2^{m+k})$, which means that there
   exists a natural number $p$ where $p * f(2^m) = f(2^{m+k})$.
   Then, $f(2^{m+k+1}) = 4^{2^{m+k+1}} + 6^{2^{m+k+1}} + 9^{2^{m+k+1}} = (4^{2^{m+k}})^2
   + (6^{2^{m+k}})^2 + (9^{2^{m+k}})^2 = f(2ˆ{m+k})^2 -  2 *(4^{2^{m+k}}*6^{2^{m+k}} +
   4^{2^{m+k}}*9^{2^{m+k}} + 6^{2^{m+k}}*9^{2^{m+k}}) \equiv -2 *
   (2^{2^{m+k}*2}*2^{2^{m+k}}*3^{2^{m+k}} + 2^{2^{m+k}*2}*3^{2^{m+k}*2} +
   2^{2^{m+k}}*3^{2^{m+k}}*3^{2^{m+k}*2} \equiv -2 * 2^{2^{m+k}}*3^{2^{m+k}} *(f(2^m)))
   \equiv 0 \pmod {f(2^m)}$.
   Hence by induction, the statement holds.
*)

Require Import Nat.
Require Import Arith.

Theorem numbertheory_fxeq4powxp6powxp9powx_f2powmdvdf2pown :
  forall (m n : nat) (f : nat -> nat),
  (forall x, f x = 4^x + 6^x + 9^x) ->
  (0 < m /\ 0 < n) ->
  m <= n ->
  exists k, f (2^n) = k * f (2^m).
Proof.
Admitted.