(* miniF2F problem: imo_1964_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose $a, b, c$ are the sides of a triangle. Prove that 

   $a^2(b+c-a)+b^2(c+a-b)+c^2(a+b-c)\le{3abc}.$

   Informal proof:
   We can use the substitution $a=x+y$, $b=x+z$, and $c=y+z$ to get

   $2z(x+y)^2+2y(x+z)^2+2x(y+z)^2\leq 3(x+y)(x+z)(y+z)$

   $2zx^2+2zy^2+2yx^2+2yz^2+2xy^2+2xz^2+12xyz\leq
   3x^2y+3x^2z+3y^2x+3y^2z+3z^2x+3z^2y+6xyz$

   $x^2y+x^2z+y^2x+y^2z+z^2x+z^2y\geq 6xyz$

   $\frac{x^2y+x^2z+y^2x+y^2z+z^2x+z^2y}{6}\geq xyz=\sqrt[6]{x^2yx^2zy^2xy^2zz^2xz^2y}$

   This is true by AM-GM. We can work backwards to get that the original inequality is
   true.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1964_p2:
  forall (a b c : R),
    0 < a /\ 0 < b /\ 0 < c ->
    c < a + b ->
    b < a + c ->
    a < b + c ->
    a² * (b + c - a) + b² * (c + a - b) + c² * (a + b - c) <= 3 * a * b * c.
Proof.
Admitted.