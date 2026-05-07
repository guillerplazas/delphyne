(* miniF2F problem: mathd_algebra_149
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let \[f(x) =
   \begin{cases}
   x^2+9 &\text{if }x<-5, \\
   3x-8&\text{if }x\ge-5.
   \end{cases}
   \]If $f(x)=10$, find the sum of all possible values of $x$. Show that it is 6.

   Informal proof:
   We begin by looking at each of the two possible cases; either $x<-5$ and
   $f(x)=x^2+9=10$, or $x\ge-5$ and $f(x)=3x-8=10$.

   Tackling the first case, we find that the only possible values of $x$ that could
   satisfy $x^2+9=10\Rightarrow x^2=1$ are 1 and -1, neither of which are less than -5,
   thus yielding no possible solutions.

   In the second case, the only possible value of $x$ that satisfies $3x-8=10$ is 6.
   Since this value is greater than or equal to -5, it satisfies both conditions. Thus,
   the only possible value of $x$ for which $f(x)=10$ is $6$, which means the sum of all
   possible values is also $6$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import List.
Require Import Sets.Finite_sets.

Open Scope R_scope.

Theorem mathd_algebra_149 :
  forall (f : R -> R),
  (forall x, x < -5 -> f x = x^2 + 5) ->
  (forall x, x >= -5 -> f x = 3 * x - 8) ->
  exists (l : list R),
    NoDup l /\
    (forall x, In x l <-> f x = 10) /\
    fold_right Rplus 0 l = 6.

Proof.
Admitted.
