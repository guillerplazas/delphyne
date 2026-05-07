(* miniF2F problem: amc12a_2020_p7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Seven cubes, whose volumes are $1$, $8$, $27$, $64$, $125$, $216$, and $343$ cubic
   units, are stacked vertically to form a tower in which the volumes of the cubes
   decrease from bottom to top. Except for the bottom cube, the bottom face of each cube
   lies completely on top of the cube below it. What is the total surface area of the
   tower (including the bottom) in square units?

   $ \textbf{(A)}\ 644\qquad\textbf{(B)}\ 658\qquad\textbf{(C)}\ 664\qquad\textbf{(D)}\
   720\qquad\textbf{(E)}\ 749 $ Show that it is \textbf{(B) }658.

   Informal proof:
   The volume of each cube follows the pattern of $n^3$, for $n$ is between $1$ and $7$.

   We see that the total surface area can be comprised of three parts: the sides of the
   cubes, the tops of the cubes, and the bottom of the $7\times 7\times 7$ cube (which
   is just $7 \times 7 = 49$). The sides areas can be measured as the sum
   $4\sum_{n=1}^{7} n^2$, giving us $560$. Structurally, if we examine the tower from
   the top, we see that it really just forms a $7\times 7$ square of area $49$.
   Therefore, we can say that the total surface area is $560 + 49 + 49 = \textbf{(B)
   }658$.
   Alternatively, for the area of the tops, we could have found the sum
   $\sum_{n=2}^{7}((n)^{2}-(n-1)^{2})$, giving us $49$ as well.

   ~ciceronii

   Note: The area on top and bottom are 49 because the largest area is 49, and the other
   cubes are ''inscribed'' in it.
*)

Require Import ZArith.
Require Import List.
Require Import Lia.

Open Scope nat_scope.

Theorem amc12a_2020_p7 :
  forall a : nat -> nat,
  (a O)^3 = 1 ->
  (a 1)^3 = 8 ->
  (a 2)^3 = 27 ->
  (a 3)^3 = 64 ->
  (a 4)^3 = 125 ->
  (a 5)^3 = 216 ->
  (a 6)^3 = 343 ->
  Z.of_nat (6 * ((a O)^2 + (a 1)^2 + (a 2)^2 + (a 3)^2 + 
                 (a 4)^2 + (a 5)^2 + (a 6)^2) - 
           2 * ((a O)^2 + (a 1)^2 + (a 2)^2 + (a 3)^2 + 
                (a 4)^2 + (a 5)^2)) = 658%Z.

Proof.
Admitted.
