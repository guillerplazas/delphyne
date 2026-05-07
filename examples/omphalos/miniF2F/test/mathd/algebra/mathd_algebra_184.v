(* miniF2F problem: mathd_algebra_184
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   We have two geometric sequences of positive real numbers: $$6,a,b\text{ and
   }\frac{1}{b},a,54$$Solve for $a$. Show that it is 3\sqrt{2}.

   Informal proof:
   Utilizing the properties of geometric sequences, we obtain: $$a^2 = 6b\text{ and }a^2
   = \frac{54}{b}.$$Thus, $6b = \frac{54}{b}$, and $b = 3.$

   Plugging that into the first equation, we have $a^2 = 18$, meaning $a = 3\sqrt{2}$
*)

Require Import Reals.
Require Import Coq.Reals.Reals.

Open Scope R_scope.

Theorem mathd_algebra_184 (a b : R)
  (h₀ : 0 < a) (h₁ : 0 < b)
  (h₂ : a^2 = 6 * b)
  (h₃ : a^2 = 54 / b) :
  a = 3 * sqrt 2.
Proof.
Admitted.