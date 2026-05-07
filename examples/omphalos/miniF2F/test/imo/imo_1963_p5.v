(* miniF2F problem: imo_1963_p5
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Prove that
   $\cos{\frac{\pi}{7}}-\cos{\frac{2\pi}{7}}+\cos{\frac{3\pi}{7}}=\frac{1}{2}$.

   Informal proof:
   Let $\cos{\frac{\pi}{7}}-\cos{\frac{2\pi}{7}}+\cos{\frac{3\pi}{7}}=S$. We have

   $S=\cos{\frac{\pi}{7}}-\cos{\frac{2\pi}{7}}+\cos{\frac{3\pi}{7}}=\cos{\frac{\pi}{7}}+\cos{\frac{3\pi}{7}}+\cos{\frac{5\pi}{7}}$

   Then, by product-sum formulae, we have

   $S * 2* \sin{\frac{\pi}{7}} =
   \sin{\frac{2\pi}{7}}+\sin{\frac{4\pi}{7}}-\sin{\frac{2\pi}{7}}+\sin{\frac{6\pi}{7}}-\sin{\frac{4\pi}{7}}=\sin{\frac{6\pi}{7}}=\sin{\frac{\pi}{7}}$

   Thus $S = 1/2$. $\blacksquare$
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1963_p5 :
  cos (PI / 7) - cos (2 * PI / 7) + cos (3 * PI / 7) = 1 / 2.
Proof.
Admitted.