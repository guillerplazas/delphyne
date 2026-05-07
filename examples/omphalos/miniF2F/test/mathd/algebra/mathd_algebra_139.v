(* miniF2F problem: mathd_algebra_139
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a \star b = \dfrac{\left(\dfrac{1}{b} - \dfrac{1}{a}\right)}{(a - b)}$, express
   $3 \star 11$ as a common fraction. Show that it is \frac{1}{33}.

   Informal proof:
   We could plug in 3 and 11 to find the answer. However, note that $a \star b =
   \dfrac{\dfrac{a - b}{ab}}{a - b} = \dfrac{1}{ab}$. Therefore, $3 \star 11 =
   \frac{1}{3 \cdot 11} = \frac{1}{33}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_139 : 
  forall s : R -> R -> R,
  (forall x y : R, x <> 0 -> y <> 0 -> s x y = (1/y - 1/x)/(x - y)) ->
  s 3 11 = 1/33.
Proof.
Admitted.