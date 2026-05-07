(* miniF2F problem: mathd_numbertheory_84
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the digit in the hundredths place of the decimal equivalent of
   $\frac{9}{160}$? Show that it is 5.

   Informal proof:
   Since the denominator of $\dfrac{9}{160}$ is $2^5\cdot5$, we multiply numerator and
   denominator by $5^4$ to obtain  \[
   \frac{9}{160} = \frac{9\cdot 5^4}{2^5\cdot 5\cdot 5^4} = \frac{9\cdot 625}{10^5} =
   \frac{5625}{10^5} = 0.05625.
   \]So, the digit in the hundredths place is $5$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope R_scope.

Theorem mathd_numbertheory_84 :
  floor ((9 / 160) * 100) = 5%Z.

Proof.
Admitted.
