(* miniF2F problem: imo_1983_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$, $b$ and $c$ be the lengths of the sides of a triangle. Prove that

   $a^2 b(a-b) + b^2 c(b-c) + c^2 a(c-a) \geq 0$.

   Determine when equality occurs.

   Informal proof:
   By Ravi substitution, let $a = y+z$, $b = z+x$, $c = x+y$. Then, the triangle
   condition becomes $x, y, z > 0$. After some manipulation, the inequality becomes:

   $xy^3 + yz^3 + zx^3 \geq xyz(x+y+z)$.

   By Cauchy, we have: 

   $(xy^3 + yz^3 + zx^3)(z+x+y) \geq xyz(y+z+x)^2$ with equality if and only if
   $\frac{xy^3}{z} = \frac{yz^3}{x} =\frac{zx^3}{y}$. So the inequality holds with
   equality if and only if x = y = z. Thus the original inequality has equality if and
   only if the triangle is equilateral.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1983_p6 : 
  forall (a b c : R),
  (0 < a /\ 0 < b /\ 0 < c) ->
  c < a + b ->
  b < a + c ->
  a < b + c ->
  0 <= a^2 * b * (a - b) + b^2 * c * (b - c) + c^2 * a * (c - a).
Proof.
Admitted.