(* miniF2F problem: amc12a_2020_p4
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many $4$-digit positive integers (that is, integers between $1000$ and $9999$,
   inclusive) having only even digits are divisible by $5?$

   $\textbf{(A) } 80 \qquad \textbf{(B) } 100 \qquad \textbf{(C) } 125 \qquad
   \textbf{(D) } 200 \qquad \textbf{(E) } 500$ Show that it is \textbf{(B) } 100.

   Informal proof:
   The units digit, for all numbers divisible by 5, must be either $0$ or $5$. However,
   since all digits are even, the units digit must be $0$. The middle two digits can be
   0, 2, 4, 6, or 8, but the thousands digit can only be 2, 4, 6, or 8 since it cannot
   be zero. There is one choice for the units digit, 5 choices for each of the middle 2
   digits, and 4 choices for the thousands digit, so there is a total of
   $4\cdot5\cdot5\cdot1 = \textbf{(B) } 100 \qquad$ numbers.
*)

Require Import Bool.
Require Import Arith.
Require Import List.
Import ListNotations.

Definition condition '(a,b,c,d) : bool :=
  Nat.even a && Nat.even b && Nat.even c && Nat.even d &&
    ((1000 * a + 100 * b + 10 * c + d) mod 5 =? 0).

Theorem amc12a_2020_p4 :
  length (filter condition
    (list_prod
       (list_prod
          (list_prod (seq 1 9) (seq 0 10))
          (seq 0 10))
       (seq 0 10))) = 100.
Proof.
Admitted.
