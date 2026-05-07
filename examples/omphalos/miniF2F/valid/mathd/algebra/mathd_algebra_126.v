(* miniF2F problem: mathd_algebra_126
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The midpoint of the line segment between $(x,y)$ and $(-9,1)$ is $(3,-5)$. Find
   $(x,y)$. Show that it is (15,-11).

   Informal proof:
   Applying the midpoint formula gives us
   $$\left(\frac{-9+x}{2},\frac{1+y}{2}\right)=(3,-5).$$Solving $\frac{-9+x}{2} =3$ for
   $x$ and solving $\frac{1+y}{2}=-5$ for $y$, we find the coordinates $(x,y)$ to be
   $(15,-11)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_126 (x y : R) :
  2 * IZR(3) = x - IZR(9) ->
  2 * IZR(-5) = y + IZR(1) ->
  x = IZR(15) /\ y = IZR(-11).

Proof.
Admitted.
