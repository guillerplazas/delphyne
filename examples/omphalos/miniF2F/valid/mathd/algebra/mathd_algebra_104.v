(* miniF2F problem: mathd_algebra_104
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   In a 8 fluid ounce bottle of Vitamin Water, there are 125 calories. How many calories
   would be contained in a 12 fluid ounce bottle? Express your answer in decimal form.
   Show that it is 187.5.

   Informal proof:
   We know that there are 125 calories in 8 fluid ounces of Vitamin Water, so we can set
   up the proportion $\frac{125}{8}=\frac{x}{12}$, where $x$ is the number of calories
   contained in a 12 fluid ounce bottle. Solving for $x$, we find that
   $x=\left(\frac{125}{8}\right)(12)=187.5$ calories.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_104 (x : R) (h0 : 125 / 8 = x / 12) : x = 375 / 2.
Proof.
Admitted.