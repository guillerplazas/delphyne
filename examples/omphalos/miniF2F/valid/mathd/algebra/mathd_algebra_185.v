(* miniF2F problem: mathd_algebra_185
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many integers are in the solution of the inequality $|x + 4|< 9$? Show that it is
   17.

   Informal proof:
   If $x+4\geq 0$ (or $x\geq -4$), then the given inequality is the same as $x+4<9$
   which means $x<5$. If $x+4<0$ (or $x<-4$), we have $-(x+4)<9$ which means $x+4>-9$
   which yields $x>-13$. Thus, the solution is $-13<x<5$. Thus, the integers in this
   solution are -1 through -12 (12 integers), 1 through 4 (4 integers), and 0 (1
   integer). Thus, the total is $12+4+1=17$ integers.
*)

Require Import ZArith.
Require Import Sets.Ensembles.
Require Import Sets.Finite_sets.

Open Scope Z_scope.

Theorem mathd_algebra_185:
  exists S : Ensemble Z,
  Finite Z S /\
  (forall x, In Z S x <-> Z.abs (x + 4) < 9) /\
  cardinal _ S (Z.to_nat 17).


Proof.
Admitted.
