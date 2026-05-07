(* miniF2F problem: imo_1981_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The function $f(x,y)$ satisfies

   (1) $f(0,y)=y+1, $

   (2) $f(x+1,0)=f(x,1), $

   (3) $f(x+1,y+1)=f(x,f(x+1,y)), $

   for all non-negative integers $x,y $. Determine $f(4,1981) $.

   Informal proof:
   We observe that $f(1,0) = f(0,1) = 2 $ and that $f(1, y+1) = f(1, f(1,y)) = f(1,y) +
   1$, so by induction, $f(1,y) = y+2 $.  Similarly, $f(2,0) = f(1,1) = 3$ and $f(2,
   y+1) = f(2,y) + 2$, yielding $f(2,y) = 2y + 3$.

   We continue with $f(3,0) + 3 = 8 $; $f(3, y+1) + 3 = 2(f(3,y) + 3)$; $f(3,y) + 3 =
   2^{y+3}$; and $f(4,0) + 3 = 2^{2^2}$; $f(4,y) + 3 = 2^{f(4,y) + 3}$.

   It follows that $f(4,1981) = 2^{2\cdot ^{ . \cdot 2}} - 3 $ when there are 1984 2s,
   Q.E.D.
*)

Require Import PeanoNat.

Theorem imo_1981_p6
  (f : nat -> nat -> nat)
  (h0 : forall y, f 0 y = y + 1)
  (h1 : forall x, f (S x) 0 = f x 1)
  (h2 : forall x y, f (S x) (S y) = f x (f (S x) y)) :
  forall y, f 4 (S y) = 2^(f 4 y + 3) - 3.
Proof.
Admitted.