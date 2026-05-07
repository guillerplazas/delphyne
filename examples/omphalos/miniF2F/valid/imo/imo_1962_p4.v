(* miniF2F problem: imo_1962_p4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve the equation $\cos^2{x}+\cos^2{2x}+\cos^2{3x}=1$.

   Informal proof:
   First, note that we can write the left hand side as a cubic function of $\cos^2 x$.
   So there are at most $3$ distinct values of $\cos^2 x$ that satisfy this equation.
   Therefore, if we find three values of $x$ that satisfy the equation and produce three
   different $\cos^2 x$, then we found all solutions to this cubic equation (without
   expanding it, which is another viable option). Indeed, we find that $\frac{\pi}2$,
   $\frac{\pi}4$, and $\frac{\pi}6$ all satisfy the equation, and produce three
   different values of $\cos^2 x$, namely $0$, $\frac12$, and $\frac34$. So we solve
   $\cos^2 x = \text{each of these}$. Therefore, our solutions are:

   $x = \frac{(2k+1)\pi}2,\, \frac{(2k+1)\pi}4,\, \frac{(6k+1)\pi}6,\, \frac{(6k+5)\pi}6
   \quad \forall k\in Z$
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem imo_1962_p4 :
  forall x : R,
    (cos x)^2 + (cos (2*x))^2 + (cos (3*x))^2 = 1 ->
      (exists m : Z, x = PI / 2 + IZR m * PI)
      \/
      (exists m : Z, x = PI / 4 + IZR m * (PI / 2))
      \/
      (exists m : Z, x = PI / 6 + IZR m * (PI / 6))
      \/
      (exists m : Z, x = 5*PI / 6 + IZR m * (PI / 6)).

Proof.
Admitted.
