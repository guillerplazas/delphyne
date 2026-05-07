(* miniF2F problem: aime_1987_p8
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the largest positive integer $n$ for which there is a unique integer $k$ such
   that $\frac{8}{15} < \frac{n}{n + k} < \frac{7}{13}$? Show that it is 112.

   Informal proof:
   Multiplying out all of the [[denominator]]s, we get:

   $\begin{align*}104(n+k) &< 195n< 105(n+k)\\
   0 &< 91n - 104k < n + k\end{align*}$

   Since $91n - 104k < n + k$, $k > \frac{6}{7}n$. Also, $0 < 91n - 104k$, so $k <
   \frac{7n}{8}$. Thus, $48n < 56k < 49n$. $k$ is unique if it is within a maximum
   [[range]] of $112$, so $n = 112$.
*)

Require Import Reals.
Require Import Nat.
Require Import Classical_Pred_Type.

(* The theorem states that 112 is the greatest positive natural number n
   for which there exists a unique k such that 8/15 < n/(n+k) < 7/13 *)
Theorem aime_1987_p8:
  forall n : nat,
  0 < n ->
  (exists! k : nat,
    (8/15 < INR n / INR (n + k))%R /\
    (INR n / INR (n + k) < 7/13)%R) ->
  n <= 112.
Proof.
Admitted.
