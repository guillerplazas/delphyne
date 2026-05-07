(* miniF2F problem: mathd_algebra_320
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $x$ be a positive number such that $2x^2 = 4x + 9.$ If $x$ can be written in
   simplified form as $\dfrac{a + \sqrt{b}}{c}$ such that $a,$ $b,$ and $c$ are positive
   integers, what is $a + b + c$? Show that it is 26.

   Informal proof:
   First, we move all terms to one side to get $2x^2 - 4x - 9 = 0.$ Seeing that
   factoring will not work, we apply the Quadratic Formula: \begin{align*}
   x &= \frac{-(-4) \pm \sqrt{(-4)^2 - 4(2)(-9)}}{2 (2)}\\
   &= \frac{4 \pm \sqrt{16 + 72}}{4} = \frac{4 \pm \sqrt{88}}{4}\\
   &= \frac{4 \pm 2\sqrt{22}}{4} = \frac{2 \pm \sqrt{22}}{2}.
   \end{align*}Since $x$ is positive, $x$ can be written as $\dfrac{2 + \sqrt{22}}{2},$
   so our answer is $2 + 22 + 2 = 26.$
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_320
  (x : R) (a b c : nat)
  (H_pos_a : (INR a > 0)%R)
  (H_pos_b : (INR b > 0)%R)
  (H_pos_c : (INR c > 0)%R)
  (H_pos_x : x >= 0)
  (H_quad : 2 * x^2 = 4 * x + 9)
  (H_repr : x = (INR a + sqrt (INR b)) / INR c)
  (H_c_val : c = 2%nat) :
  (INR (a + b + c) = 26)%R.

Proof.
Admitted.
