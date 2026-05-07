(* miniF2F problem: mathd_algebra_144
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many distinct, non-equilateral triangles with a perimeter of 60 units have
   integer side lengths $a$, $b$, and $c$ such that $a$, $b$, $c$ is an arithmetic
   sequence? Show that it is 9.

   Informal proof:
   Let $d$ be the common difference, so $a = b - d$ and $c = b + d$.  We can assume that
   $d$ is positive.  (In particular, $d$ can't be 0, because the triangle is not
   equilateral.)  Then the perimeter of the triangle is $a + b + c = (b - d) + b + (b +
   d) = 3b = 60$, so $b = 20$.  Hence, the sides of the triangle are $20 - d$, 20, and
   $20 + d$.

   These sides must satisfy the triangle inequality, which gives us \[(20 - d) + 20 > 20
   + d.\] Solving for $d$, we find $2d < 20$, or $d < 10$.  Therefore, the possible
   values of $d$ are 1, 2, $\dots$, 9, which gives us $9$ possible triangles.
*)

Require Import Arith.PeanoNat.

Theorem mathd_algebra_144
  (a b c d : nat)
  (h0 : 0 < a) (h1 : 0 < b) (h2 : 0 < c) (h3 : 0 < d)
  (h4 : c - b = d)
  (h5 : b - a = d)
  (h6 : a + b + c = 60)
  (h7 : a + b > c) :
  d < 10.
Proof.
Admitted.