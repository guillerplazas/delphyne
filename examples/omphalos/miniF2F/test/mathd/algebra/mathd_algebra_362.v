(* miniF2F problem: mathd_algebra_362
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a$ and $b$ are real numbers, $a^2b^3=\frac{32}{27}$, and
   $\frac{a}{b^3}=\frac{27}{4}$, what is $a+b$? Show that it is \frac83.

   Informal proof:
   Rearranging the second equation, we have that $b^3=\frac{4}{27}a$. If we substitute
   this into the original equation, we get $\frac{4}{27}a^3=\frac{32}{27}$; after
   multiplying each side by $\frac{27}{4}$ and taking the cube root, we see that $a=2$.
   Substituting $a$ into the first equation, we get that $b^3=\frac{8}{27}$ or
   $b=\frac23$. Thus, $a+b=2+\frac23=\frac83$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_362:
  forall (a b : R),
  a^2 * b^3 = 32 / 27 ->
  a / b^3 = 27 / 4 ->
  a + b = 8 / 3.
Proof.
Admitted.