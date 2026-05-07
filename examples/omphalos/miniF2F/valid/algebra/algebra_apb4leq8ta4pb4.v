(* miniF2F problem: algebra_apb4leq8ta4pb4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any positive real numbers $a$ and $b$, $(a+b)^4 \leq 8(a^4 + b^4)$.

   Informal proof:
   Re-arranging, we must prove $(\frac{a+b}{2})^4\leq\frac{a^4 + b^4}{2}$. We prove the
   more general statement $(\frac{a+b}{2})^n\leq\frac{a^n + b^n}{2}$ for integers $n >
   0$ by induction.
   The result is trivial for $n=1$. Let us assume the property holds for $n \geq 1$.
   We have that $\left(\frac{a+b}{2}\right)^{n+1} = \left(\frac{a+b}{2}\right)^n
   \frac{a+b}{2} \leq \frac{a^n+b^n}{2} \frac{a+b}{2}$
   However, $\frac{a^{n+1}+b^{n+1}}{2} - \frac{a^n+b^n}{2} \frac{a+b}{2} = \frac{(a^n -
   b^n)(a-b)}{4}$.
   $a^n - b^n$ and $a-b$ have the same sign so $\frac{(a^n - b^n)(a-b)}{4} \geq 0$ and
   $\frac{(a^n - b^n)(a-b)}{4} \geq 0$.
   As a result, $\left(\frac{a+b}{2}\right)^{n+1} \leq \frac{a^{n+1}+b^{n+1}}{2}$ and
   the property holds in $n+1$.
   By induction, the result is true for any natural number $n \geq 1$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_apb4leq8ta4pb4 :
  forall a b : R, (0 < a) -> (0 < b) -> (a + b)^4 <= 8 * (a^4 + b^4).
Proof.
Admitted.