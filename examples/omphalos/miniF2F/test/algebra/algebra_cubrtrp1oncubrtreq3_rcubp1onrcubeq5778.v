(* miniF2F problem: algebra_cubrtrp1oncubrtreq3_rcubp1onrcubeq5778
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $r$ be a real number such that $r^{\frac{1}{3}} + \frac{1}{r^{\frac{1}{3}}} = 3$.
   Show that $r^3 + \frac{1}{r^3} = 5778$.

   Informal proof:
   Cubing both sides, we get $(r^{\frac{1}{3}} + \frac{1}{r^{\frac{1}{3}}})^3 = r +
   \frac{1}{r} + 3 r^{\frac{1}{3}} + 3 \frac{1}{r^{\frac{1}{3}}} = r + \frac{1}{r} + 3
   \times 3 = 3^3 = 27$.
   Therefore we get that $r + \frac{1}{r} = 27-9 = 18$. 
   Then taking the cube of both sides of the new equation, we get $(r + \frac{1}{r})^3 =
   r^3 + \frac{1}{r^3} + 3r + 3\frac{1}{r} = r^3 + \frac{1}{r^3} + 3 \times 18 = 18^3
   =5832$. Hence $r^3 + \frac{1}{r^3} = 5832-54 = 5778$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope R_scope.

Theorem algebra_cubrtrp1oncubrtreq3_rcubp1onrcubeq5778 :
  forall r : R,
  Rpower r (1/3) + (1 / Rpower r (1/3)) = 3 ->
  r^3 + (1 / r^3) = 5778.

Proof.
Admitted.
