(* miniF2F problem: mathd_algebra_392
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The sum of the squares of three consecutive positive even numbers is $12296$. Find
   the product of the three numbers divided by $8$. Show that it is 32736.

   Informal proof:
   If $n$ is the middle number of the three, the other two numbers are $n-2$ and $n+2$.
   Therefore, the squares are $n^2-4n+4$, $n^2$, and $n^2+4n+4$. Setting the sum of the
   three squares equal to $12296$, \begin{align*}
   \left(n^2-4n+4\right)+\left(n^2\right)+\left(n^2+4n+4\right)&=12296\\
   3n^2+8&=12296\\
   3n^2&=12288\\
   n^2&=4096\\
   n&=\pm64
   \end{align*}Because $n$ is positive, $n$ must be $64$. Therefore, the set of numbers
   is $62, 64, 66$. The product of those is $261888$. The product divided by 8 is
   $32736$.
*)

Require Import Arith.
Require Import Lia.

Theorem mathd_algebra_392 :
  forall (n : nat),
    Nat.even n = true ->
    n^2 + (n + 2)^2 + (n + 4)^2 = 12296 ->
    (n * (n + 2) * (n + 4)) / 8 = 32736.
Proof.
Admitted.
