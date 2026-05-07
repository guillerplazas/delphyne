(* miniF2F problem: aime_1988_p4
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $|x_i| < 1$ for $i = 1, 2, \dots, n$.  Suppose further that
   $
   |x_1| + |x_2| + \dots + |x_n| = 19 + |x_1 + x_2 + \dots + x_n|.
   $
   What is the smallest possible value of $n$? Show that it is 020.

   Informal proof:
   Since $|x_i| < 1$ then

   $|x_1| + |x_2| + \dots + |x_n| = 19 + |x_1 + x_2 + \dots + x_n| < n.$

   So $n \ge 20$. We now just need to find an example where $n = 20$: suppose $x_{2k-1}
   = \frac{19}{20}$ and $x_{2k} = -\frac{19}{20}$; then on the left hand side we have
   $\left|\frac{19}{20}\right| + \left|-\frac{19}{20}\right| + \dots +
   \left|-\frac{19}{20}\right| = 20\left(\frac{19}{20}\right) = 19$. On the right hand
   side, we have $19 + \left|\frac{19}{20} - \frac{19}{20} + \dots -
   \frac{19}{20}\right| = 19 + 0 = 19$, and so the equation can hold for $n = 020$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem aime_1988_p4 :
  forall (n : nat) (a : nat -> R),
  (forall k, (k < n)%nat -> Rabs (a k) < 1) ->
  sum_f_R0 (fun k => Rabs (a k)) (pred n) = 19 + Rabs (sum_f_R0 (fun k => a k) (pred n)) ->
  (20 <= n)%nat.

Proof.
Admitted.
