(* miniF2F problem: amc12a_2021_p3
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of two natural numbers is $17{,}402$. One of the two numbers is divisible by
   $10$. If the units digit of that number is erased, the other number is obtained. What
   is the difference of these two numbers?

   $\textbf{(A)} ~10{,}272\qquad\textbf{(B)} ~11{,}700\qquad\textbf{(C)}
   ~13{,}362\qquad\textbf{(D)} ~14{,}238\qquad\textbf{(E)} Show that it is \textbf{(D)}
   ~14{,}238.

   Informal proof:
   The units digit of a multiple of $10$ will always be $0$. We add a $0$ whenever we
   multiply by $10$. So, removing the units digit is equal to dividing by $10$.

   Let the smaller number (the one we get after removing the units digit) be $a$. This
   means the bigger number would be $10a$.

   We know the sum is $10a+a = 11a$ so $11a=17402$. So $a=1582$. The difference is
   $10a-a = 9a$. So, the answer is $9(1582) = \textbf{(D)} ~14{,}238$.
*)

Require Import ZArith.
Require Import Nat.
Require Import Lia.

Theorem amc12a_2021_p3:
  forall (x y : nat),
  x + y = 17402 ->
  (exists k, x = 10 * k)%nat ->
  (x / 10 = y)%nat ->
  (Z.of_nat x - Z.of_nat y = 14238)%Z.

Proof.
Admitted.
