(* miniF2F problem: mathd_algebra_170
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many integers are in the solution set of $|x-2|\leq5.6$ ? Show that it is 11.

   Informal proof:
   Getting rid of the absolute value, we have $-5.6 \le x-2 \le 5.6$, or $-3.6 \le x \le
   7.6$. Thus, $x$ can be any integer from -3 to 7, inclusive. There are $7-(-3)+1=11$
   integers in this range.
*)

Require Import Reals.
Require Import ZArith.
Require Import List.
Require Import SetoidList.

Open Scope R_scope.

Theorem mathd_algebra_170:
  forall (S: list Z),
    NoDup S ->
    (forall n:Z, In n S <-> (Rabs (IZR n - 2) <= 5.6)%R) ->
    length S = 11%nat.

Proof.
Admitted.
