(* miniF2F problem: aime_1997_p11
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $x=\frac{\sum\limits_{n=1}^{44} \cos n^\circ}{\sum\limits_{n=1}^{44} \sin
   n^\circ}$. What is the greatest integer that does not exceed $100x$? Show that it is
   241.

   Informal proof:
   A slight variant of the above solution, note that 

   $$\begin{eqnarray*}
   \sum_{n=1}^{44} \cos n + \sum_{n=1}^{44} \sin n &=& \sum_{n=1}^{44} \sin n +
   \sin(90-n)\\
   &=& \sqrt{2}\sum_{n=1}^{44} \cos(45-n) = \sqrt{2}\sum_{n=1}^{44} \cos n\\
   \sum_{n=1}^{44} \sin n &=& (\sqrt{2}-1)\sum_{n=1}^{44} \cos n
   \end{eqnarray*}$$

   This is the [[ratio]] we are looking for. $x$ reduces to $\frac{1}{\sqrt{2} - 1} =
   \sqrt{2} + 1$, and $\lfloor 100(\sqrt{2} + 1)\rfloor = 241$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import Lia.

Open Scope R_scope.

Definition degree (x : R) : R := (x * PI / 180).

Theorem aime_1997_p11 :
  forall x : R,
  x = (sum_n_m (fun n => cos (degree (INR n))) 1 44) /
      (sum_n_m (fun n => sin (degree (INR n))) 1 44) ->
  floor (100 * x) = 241%Z.

Proof.
Admitted.
