(* miniF2F problem: imo_2006_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real numbers $a$, $b$, and $c$, we have $(ab(a^2 - b^2)) + (bc(b^2
   - c^2)) + (ca(c^2 - a^2)) \leq \frac{9\sqrt{2}}{32}(a^2 + b^2 + c^2)^2$.

   Informal proof:
   It's the same as
   $$|(a-b)(b-c)(c-a)(a+b+c)| \leq M\left(a^2+b^2+c^2\right)^2$$
   Let $x=a-b, y=b-c, z=c-a, s=a+b+c$. Then we want to have
   $$|x y z s| \leq \frac{M}{9}\left(x^2+y^2+z^2+s^2\right)^2$$
   Here $x+y+z=0$.
   Now if $x$ and $y$ have the same sign, we can replace them with the average (this
   increases the LHS and decreases RHS). So we can have $x=y, z=-2 x$. Now WLOG $x>0$ to
   get
   $$2 x^3 \cdot s \leq \frac{M}{9}\left(6 x^2+s^2\right)^2$$
   After this routine calculation gives $M=\frac{9}{32} \sqrt{2}$ works and is optimal
   (by $6 x^2+s^2=$ $2 x^2+2 x^2+2 x^2+s^2$ and AM-GM).
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_2006_p3 (a b c : R) :
  (a * b * (a^2 - b^2)) + (b * c * (b^2 - c^2)) + (c * a * (c^2 - a^2)) <= (9 * sqrt 2) / 32 * (a^2 + b^2 + c^2)^2.
Proof.
Admitted.