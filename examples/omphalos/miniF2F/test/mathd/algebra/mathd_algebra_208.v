(* miniF2F problem: mathd_algebra_208
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of $\sqrt{1,\!000,\!000} - \sqrt[3]{1,\!000,\!000}$? Show that it
   is 900.

   Informal proof:
   We have   \begin{align*}
   \sqrt{1,\!000,\!000} - \sqrt[3]{1,\!000,\!000}&= \sqrt{10^6} - \sqrt[3]{10^6} \\
   &= (10^6)^{\frac{1}{2}} - (10^6)^{\frac{1}{3}}\\
   &=10^{6\cdot \frac{1}{2}} - 10^{6\cdot \frac{1}{3}} \\
   &= 10^3 - 10^2 = 1000-100 =900.
   \end{align*}
*)

Require Import Reals.

Open Scope R_scope.

Theorem mathd_algebra_208 :
  sqrt 1000000 - Rpower 1000000 (1/3) = 900.

Proof.
Admitted.
