(* miniF2F problem: imo_1966_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve the system of equations

   $|a_1 - a_2| x_2 +|a_1 - a_3| x_3 +|a_1 - a_4| x_4 = 1\\ |a_2 - a_1| x_1 +|a_2 - a_3|
   x_3 +|a_2 - a_4| x_4 = 1\\ |a_3 - a_1| x_1 +|a_3 - a_2| x_2 +|a_3-a_4|x_4= 1\\ |a_4 -
   a_1| x_1 +|a_4 - a_2| x_2 +|a_4 - a_3| x_3 = 1$

   where $a_1, a_2, a_3, a_4$ are four different real numbers.

   Informal proof:
   Take a1 > a2 > a3 > a4. Subtracting the equation for i=2 from that for i=1 and
   dividing by (a1 - a2) we get:

   $- x1 + x2 + x3 + x4 = 0.$

   Subtracting the equation for i=4 from that for i=3 and dividing by (a3 - a4) we get:

   $- x1 - x2 - x3 + x4 = 0.$

   Hence x1 = x4. Subtracting the equation for i=3 from that for i=2 and dividing by (a2
   - a3) we get:

   $- x1 - x2 + x3 + x4 = 0.$

   Hence $x2 = x3 = 0$, and $x1 = x4 = 1/(a1 - a4)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1966_p5 (x a : nat -> R)
  (H0 : a (S O) > a (S (S O)))
  (H1 : a (S (S O)) > a (S (S (S O))))
  (H2 : a (S (S (S O))) > a (S (S (S (S O)))))
  (H3 : Rabs (a (S O) - a (S (S O))) * x (S (S O)) +
        Rabs (a (S O) - a (S (S (S O)))) * x (S (S (S O))) +
        Rabs (a (S O) - a (S (S (S (S O))))) * x (S (S (S (S O)))) = R1)
  (H4 : Rabs (a (S (S O)) - a (S O)) * x (S O) +
        Rabs (a (S (S O)) - a (S (S (S O)))) * x (S (S (S O))) +
        Rabs (a (S (S O)) - a (S (S (S (S O))))) * x (S (S (S (S O)))) = R1)
  (H5 : Rabs (a (S (S (S O))) - a (S O)) * x (S O) +
        Rabs (a (S (S (S O))) - a (S (S O))) * x (S (S O)) +
        Rabs (a (S (S (S O))) - a (S (S (S (S O))))) * x (S (S (S (S O)))) = R1)
  (H6 : Rabs (a (S (S (S (S O)))) - a (S O)) * x (S O) +
        Rabs (a (S (S (S (S O)))) - a (S (S O))) * x (S (S O)) +
        Rabs (a (S (S (S (S O)))) - a (S (S (S O)))) * x (S (S (S O))) = R1) :
  x (S (S O)) = R0 /\
  x (S (S (S O))) = R0 /\
  x (S O) = R1 / Rabs (a (S O) - a (S (S (S (S O))))) /\
  x (S (S (S (S O)))) = R1 / Rabs (a (S O) - a (S (S (S (S O))))).
Proof.
Admitted.

Theorem imo_1966_p5':
  forall (m n : nat) (x a : nat -> R),
  (forall i j, a i = a j -> i = j) ->
  (Rabs (a 1%nat - a 2%nat) * x 2%nat + Rabs (a 1%nat - a 3%nat) * x 3%nat + Rabs (a 1%nat - a 4%nat) * x 4%nat = INR 1) ->
  (Rabs (a 2%nat - a 1%nat) * x 1%nat + Rabs (a 2%nat - a 3%nat) * x 3%nat + Rabs (a 2%nat - a 4%nat) * x 4%nat = INR 1) ->
  (Rabs (a 3%nat - a 1%nat) * x 1%nat + Rabs (a 3%nat - a 2%nat) * x 2%nat + Rabs (a 3%nat - a 4%nat) * x 4%nat = INR 1) ->
  (Rabs (a 4%nat - a 1%nat) * x 1%nat + Rabs (a 4%nat - a 2%nat) * x 2%nat + Rabs (a 4%nat - a 3%nat) * x 3%nat = INR 1) ->
  (1<= m <= 4 )%nat -> (1<= n <= 4)%nat -> (forall i : nat, a m >= a i) ->
  (forall i, a n <= a i) ->
  (x m = 1/ (a m - a n)) /\ (x n = x m) /\ (forall i : nat , (i<=4)%nat -> i <> m -> i <> n -> x i = R0).
Proof.
Admitted.
