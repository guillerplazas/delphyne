(* miniF2F problem: amc12b_2004_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $x$ and $y$ are positive integers for which $2^x3^y=1296$, what is the value of
   $x+y$?

   $(\mathrm {A})\ 8 \qquad (\mathrm {B})\ 9 \qquad (\mathrm {C})\ 10 \qquad (\mathrm
   {D})\ 11 \qquad (\mathrm {E})\ 12$ Show that it is 8.

   Informal proof:
   $1296 = 2^4 3^4$ and $4+4=8 \Longrightarrow \mathrm{(A)}$.
*)

Require Import Arith.

Theorem amc12b_2004_p3:
  forall x y : nat,
  2^x * 3^y = 1296 -> x + y = 8.
Proof.
Admitted.