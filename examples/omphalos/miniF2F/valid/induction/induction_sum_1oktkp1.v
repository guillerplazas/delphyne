(* miniF2F problem: induction_sum_1oktkp1
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for positive integer $n$, $\sum_{k=0}^{n-1} \frac{1}{(k+1)(k+2)} =
   \frac{n}{n+1}$.

   Informal proof:
   We show the result by induction. The result is trivial for $n=1$. Let us assume the
   result holds for $n \geq 1$. Then, we have $\sum_{k=0}^{(n+1)-1} \frac{1}{(k+1)(k+2)}
   = \frac{n}{n+1} + \frac{1}{(n+1)(n+2)} = \frac{n(n+2)+1}{(n+1)(n+2)} =
   \frac{n^2+2n+1}{(n+1)(n+2)} = \frac{(n+1)^2}{(n+1)(n+2)} = \frac{n+1}{n+2}$. So the
   result holds for $n+1$, and by induction it is true for every positive integer $n$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem induction_sum_1oktkp1 :
  forall (n : nat),
    (1 <= n)%nat ->
    (sum_f_R0 (fun k => / (INR (k + 1) * INR (k + 2))) (n - 1)) = (INR n) / (INR n + 1).

Proof.
Admitted.
