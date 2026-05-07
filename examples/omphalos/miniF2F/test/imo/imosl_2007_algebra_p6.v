(* miniF2F problem: imosl_2007_algebra_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For a series $\{a_n\}$, we have $\sum_{n=0}^{99} a_{n+1}^2 = 1$. Show that
   $\sum_{n=0}^{98} (a_{n+1}^2 a_{n+2}) + a_{100}^2 * a_1 < \frac{12}{25}$.

   Informal proof:
   Using the Cauchy-Schwarz inequality we can bound the left-hand side in the following
   way:
   \begin{align*}
   & \frac{1}{3}\left[a_1(a_{100}^2+2a_1 a_2) + a_2(a_1^2 + 2a_2 a_3) + \cdots +
   a_{100}(a_{99}^2 + 2a_{100} a_1)\right] \\
   \leq & \frac{1}{3} 
   \sqrt{\left(a_1^2 + a_2^2 + \cdots + a_{100}^2\right)
   \left(\displaystyle\sum_{k=1}^{100}\left(a_k^2+2a_{k+1}a_{k+2}\right)\right)}
   \text{(the indeces are modulo 100)}\\
   = &
   \frac{1}{3}\sqrt{\left(\displaystyle\sum_{k=1}^{100}\left(a_k^2+2a_{k+1}a_{k+2}\right)\right)}
   \end{align*}
   It suffices to show 
   \begin{align*}
   \displaystyle\sum_{k=1}^{100}\left(a_k^2+2a_{k+1}a_{k+2}\right)^2 \leq 2.
   \end{align*}
   Each term of the last sum can be seen 
   \begin{align*}
   & a_k^4+4a_{k+1}^2 a_{k+2}^2+4a_k^2\left(a_{k+1}a_{k+2}\right) \\
   \leq & \left(a_k^4 + 2a_k^2a_{k+1}^2 + 2a_k^2a_{k+2}^2\right) + 4a_{k+1}^2a_{k+2}^2.
   \end{align*}
   The required inequality now follows from
   \begin{align*}
   & \displaystyle\sum_{k=1}^{100}\left(a_k^4 + 2a_k^2a_{k+1}^2 + 2a_k^2a_{k+2}^2\right)
   \\
   \leq & \left(\displaystyle\sum_{k=1}^{100} a_k^2\right)^2 = 1
   \end{align*}
   and
   \begin{align*}
   & \displaystyle\sum_{k=1}^{100}\left(a_{k+1}^2a_{k+2}^2\right) \\
   \leq & \left(a_1^2 + a_3^2 + \cdots + a_{99}^2\right) \left(a_2^2 + a_4^2 + \cdots +
   a_{100}^2\right) \\
   \leq & \frac{1}{4}\left(a_1^2 + a_2^2 + \cdots + a_{100}^2\right)^2 \\
   = & \frac{1}{4}.
   \end{align*}
*)

Require Import Reals.
Require Import Psatz.
Require Import List.

Theorem imosl_2007_algebra_p6 :
  forall (a : nat -> R),
  (sum_f_R0 (fun x => (a (S x))^2) 99 = 1)%R ->
  (sum_f_R0 (fun x => (a (S x))^2 * a (S (S x))) 98 + (a 100%nat)^2 * a 1%nat < 12/25)%R.

Proof.
Admitted.
