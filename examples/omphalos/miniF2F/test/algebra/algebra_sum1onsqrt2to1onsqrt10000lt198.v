(* miniF2F problem: algebra_sum1onsqrt2to1onsqrt10000lt198
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that $\sum_{k=2}^{10000} \frac{1}{\sqrt{k}} < 198$.

   Informal proof:
   For every $k$ such that $2 \leq k \leq 10000$, $\frac{1}{\sqrt{k}} < \int_{k-1}^{k}
   \frac{1}{\sqrt{t}} \,dt$.
   As a result, $\sum_{k=2}^{10000}\frac{1}{\sqrt{k}} < \sum_{k=2}^{10000}
   \int_{k-1}^{k} \frac{1}{\sqrt{t}} \,dt = \int_{1}^{10000} \frac{1}{\sqrt{t}}
   \,dt$.Since $\int_{1}^{10000} \frac{1}{\sqrt{t}} \,dt = 2 (\sqrt{10000} - \sqrt{1}) =
   198$, we have $\sum_{k=2}^{10000} \frac{1}{\sqrt{k}} < 198$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem algebra_sum1onsqrt2to1onsqrt10000lt198 :
  sum_f_R0 (fun i => 1 / sqrt (INR (i + 2))) 9998 < 198.

Proof.
Admitted.
