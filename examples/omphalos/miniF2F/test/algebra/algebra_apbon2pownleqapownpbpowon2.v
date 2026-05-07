(* miniF2F problem: algebra_apbon2pownleqapownpbpowon2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be two positive real numbers, and $n$ be a positive integer. Show
   that $(\frac{a+b}{2})^n \leq \frac{a^n+b^n}{2}$.

   Informal proof:
   We show the result by induction on $n$. The result is trivial for $n=1$. Let us
   assume the property holds for $n \geq 1$.
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

Require Import Coq.Reals.Reals.
Open Scope R_scope.

Theorem algebra_apbon2pownleqapownpbpowon2 :
  forall (a b : R) (n : nat),
    0 < a ->
    0 < b ->
    (0 < n)%nat ->
    ((a + b) / 2)^n <= (a ^ n + b ^ n) / 2.

Proof.
Admitted.
