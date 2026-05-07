(* miniF2F problem: algebra_xmysqpymzsqpzmxsqeqxyz_xpypzp6dvdx3y3z3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let x, y, and z be integers. If $(x-y)^2 + (y-z)^2 + (z-x)^2 = xyz$, then $(x+y+z+6)$
   divides $(x^3 + y^3 + z^3)$.

   Informal proof:
   We have $x^3 + y^3 + z^3 - 3xyz = (x+y+z)(x^2+y^2+z^2-xy-xz-yz) =
   \frac{1}{2}(x+y+z)\left((x-y)^2+(y-z)^2+(z-x)^2\right)$.
   Using the hypothesis,  $x^3 + y^3 + z^3 - 3xyz = \frac{xyz}{2}(x+y+z)$. Thus, $x^3 +
   y^3 + z^3 = \frac{(x+y+z+6)(xyz)}{2}$.
   Finally, since $xyz = (x-y)^2 + (y-z)^2 + (z-x)^2 = 2(x^2+y^2+z^2-xy-xz-yz)$: so
   $xyz=2k$ for some integer $k$ and we have $x^3 + y^3 + z^3 = k(x+y+z+6)$, which
   completes the proof.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem algebra_xmysqpymzsqpzmxsqeqxyz_xpypzp6dvdx3y3z3:
  forall (x y z : Z),
  (Z.pow (x - y) 2) + (Z.pow (y - z) 2) + (Z.pow (z - x) 2) = x * y * z ->
  Z.divide (x + y + z + 6) (Z.pow x 3 + Z.pow y 3 + Z.pow z 3).

Proof.
Admitted.
