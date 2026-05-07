(* miniF2F problem: aimeII_2001_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given that

   $$
   \begin{align*}x_{1}&=211,\\
   x_{2}&=375,\\
   x_{3}&=420,\\
   x_{4}&=523,\ \text{and}\\
   x_{n}&=x_{n-1}-x_{n-2}+x_{n-3}-x_{n-4}\ \text{when}\ n\geq5, \end{align*}
   $$

   find the value of $x_{531}+x_{753}+x_{975}$. Show that it is 898.

   Informal proof:
   We find that $x_5 = 267$ by the recursive formula. Summing the [[recursion]]s

   $$\begin{align*}
   x_{n}&=x_{n-1}-x_{n-2}+x_{n-3}-x_{n-4} \\
   x_{n-1}&=x_{n-2}-x_{n-3}+x_{n-4}-x_{n-5}
   \end{align*}$$

   yields $x_{n} = -x_{n-5}$. Thus $x_n = (-1)^k x_{n-5k}$. Since $531 = 106 \cdot 5 +
   1,\ 753 = 150 \cdot 5 + 3,\ 975 = 194 \cdot 5 + 5$, it follows that

   $$x_{531} + x_{753} + x_{975} = (-1)^{106} x_1 + (-1)^{150} x_3 + (-1)^{194} x_5 =
   211 + 420 + 267 = 898.$$
*)

Require Import ZArith.
Require Import Nat.

Theorem aimeII_2001_p3 :
  forall (x : nat -> Z),
    x 1%nat = 211%Z ->
    x 2%nat = 375%Z ->
    x 3%nat = 420%Z ->
    x 4%nat = 523%Z ->
    (forall n : nat, (n >= 5)%nat -> 
      x n = (x (n - 1)%nat - x (n - 2)%nat + x (n - 3)%nat - x (n - 4)%nat)%Z) ->
    (x 531%nat + x 753%nat + x 975%nat)%Z = 898%Z.

Proof.
Admitted.
