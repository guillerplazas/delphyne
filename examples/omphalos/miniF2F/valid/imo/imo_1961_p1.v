(* miniF2F problem: imo_1961_p1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   (''Hungary'')
   Solve the system of equations:

   <center>
   $
   \begin{matrix}
   \quad x + y + z \!\!\! &= a \; \, \\
   x^2 +y^2+z^2 \!\!\! &=b^2 \\
   \qquad \qquad xy \!\!\!  &= z^2
   \end{matrix}
   $
   </center>

   where $a $ and $b $ are constants.  Give the conditions that $a $ and $b $ must
   satisfy so that $x, y, z $ (the solutions of the system) are distinct positive
   numbers.

   Informal proof:
   Note that $x^2 + y^2 = (x+y)^2 - 2xy = (x+y)^2 - 2z^2 $, so the first two equations
   become
   <center>
   $
   \begin{matrix}
   \quad (x + y) + z \!\!\! &= a \; \; ( * ) \\
   (x+y)^2 - z^2 \!\!\! &=b^2 ( ** )
   \end{matrix}
   $.
   </center>

   We note that $(x+y)^2 - z^2 = \Big[ (x+y)+z \Big]\Big[ (x+y)-z\Big] $, so if $a $
   equals 0, then $b $ must also equal 0.  We then have $ x+y = -z $; $xy = (x+y)^2 $. 
   This gives us $x^2 + xy + y^2 = 0 $.  Mutiplying both sides by $(x-y) $, we have $x^3
   - y^3 = 0 $.  Since we want $x,y $ to be real, this implies $x = y $.  But $x^2 + x^2
   + x^2 $ can only equal 0 when $x=0 $ (which, in this case, implies $y,z = 0 $). 
   Hence there are no positive solutions when $a = 0 $.

   When $a \neq 0 $, we divide $( ** ) $ by $( * ) $ to obtain the system of equations
   <center>
   $
   \begin{matrix}
   (x+y)+z &= a \; \quad \\
   (x+y)-z &= b^2/a
   \end{matrix}
   $,
   </center>
   which clearly has solution $ x+y = \frac{a^2 + b^2}{2a} $, $ z = \frac{a^2 - b^2}{2a}
   $.  In order for these both to be positive, we must have positive $a $ and $a^2 > b^2
   $.  Now, we have $ x+y = \frac{a^2 + b^2}{2a} $; $ xy = \left(\frac{a^2 -
   b^2}{2a}\right)^2 $, so $x,y $ are the roots of the quadratic $ m^2 - \frac{a^2 +
   b^2}{2a}m + \left(\frac{a^2 - b^2}{2a}\right)^2 $.  The [[discriminant]] for this
   equation is
   <center>
   $
   \left(\frac{a^2 + b^2}{2a}\right)^2 - \left(2\frac{a^2 -b^2}{2a}\right)^2 = \frac{
   (3a^2 - b^2)(3b^2 - a^2) }{4a^2}
   $.
   </center>
   If the expressions $(3a^2 - b^2), (3b^2 - a^2) $ were simultaneously negative, then
   their sum, $2(a^2 + b^2) $, would also be negative, which cannot be.  Therefore our
   quadratic's discriminant is positive when $3a^2 > b^2 $ and $3b^2 > a^2 $.  But we
   have already replaced the first inequality with the sharper bound $a^2 > b^2 $.  It
   is clear that both roots of the quadratic must be positive if the discriminant is
   positive (we can see this either from $ \left(\frac{a^2 + b^2}{2a}\right)^2 >
   \left(\frac{a^2 + b^2}{2a}\right)^2 - \left(2\frac{a^2 -b^2}{2a}\right)^2 $ or from
   [[Polynomial#Descartes.27_Law_of_Signs | Descartes' Rule of Signs]]).  We have now
   found the solutions to the system, and determined that it has positive solutions if
   and only if $a $ is positive and $3b^2 > a^2 > b^2 $.  Q.E.D.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1961_p1:
  forall (x y z a b : R),
  0 < x -> 0 < y -> 0 < z ->
  x <> y ->
  y <> z ->
  z <> x ->
  x + y + z = a ->
  x^2 + y^2 + z^2 = b^2 ->
  x * y = z^2 ->
  (0 < a /\ b^2 < a^2 /\ a^2 < 3 * b^2).
Proof.
Admitted.
