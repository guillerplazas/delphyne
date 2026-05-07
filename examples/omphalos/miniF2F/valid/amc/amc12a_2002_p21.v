(* miniF2F problem: amc12a_2002_p21
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Consider the sequence of numbers: $4,7,1,8,9,7,6,\dots$ For $n>2$, the $n$-th term of
   the sequence is the units digit of the sum of the two previous terms. Let $S_n$
   denote the sum of the first $n$ terms of this sequence. The smallest value of $n$ for
   which $S_n>10,000$ is: 

   $
   \text{(A) }1992
   \qquad
   \text{(B) }1999
   \qquad
   \text{(C) }2001
   \qquad
   \text{(D) }2002
   \qquad
   \text{(E) }2004
   $ Show that it is (B)1999.

   Informal proof:
   The sequence is infinite. As there are only $100$ pairs of digits, sooner or later a
   pair of consecutive digits will occur for the second time. As each next digit only
   depends on the previous two, from this point on the sequence will be periodic.

   (Additionally, as every two consecutive digits uniquely determine the <i>previous</i>
   one as well, the first pair of digits that will occur twice must be the first pair
   $4,7$.)

   Hence it is a good idea to find the period. Writing down more terms of the sequence,
   we get:

   $4,7,1,8,9,7,6,3,9,2,1,3,4,7,\dots$

   and we found the period. The length of the period is $12$, and its sum is
   $4+7+\cdots+1+3 = 60$. Hence for each $k$ we have $S_{12k} = 60k$.

   We have $\lfloor 10000/60 \rfloor = 166$ and $166\cdot 12 = 1992$, therefore
   $S_{1992} = 60\cdot 166 = 9960$.
   The rest can now be computed by hand, we get $S_{1998} = 9960+4+7+1+8+9+7= 9996$, and
   $S_{1999}=9996 + 6 = 10002$, thus the answer is $(B)1999$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.Reals.Reals.
Require Import Coq.Reals.Rdefinitions.
Require Import Coq.Lists.List.
Import ListNotations.

Theorem amc12a_2002_p21
  (u : nat -> nat)
  (h0 : u 0 = 4)
  (h1 : u 1 = 7)
  (h2 : forall n, u (n + 2) = (u n + u (n + 1)) mod 10) :
  forall n, (fold_right plus 0 (map u (seq 0 n))) > 10000 -> 1999 <= n.
Proof.
Admitted.
