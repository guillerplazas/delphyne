(* miniF2F problem: amc12b_2020_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Teams $A$ and $B$ are playing in a basketball league where each game results in a win
   for one team and a loss for the other team. Team $A$ has won $\tfrac{2}{3}$ of its
   games and team $B$ has won $\tfrac{5}{8}$ of its games. Also, team $B$ has won $7$
   more games and lost $7$ more games than team $A.$ How many games has team $A$ played?

   $\textbf{(A) } 21 \qquad \textbf{(B) } 27 \qquad \textbf{(C) } 42 \qquad \textbf{(D)
   } 48 \qquad \textbf{(E) } 63$ Show that it is \textbf{(C) } 42.

   Informal proof:
   Suppose team $A$ has played $g$ games in total so that it has won $\frac23g$ games.
   It follows that team $B$ has played $g+14$ games in total so that it has won
   $\frac23g+7$ games.

   We set up and solve an equation for team $B$'s win ratio:
   $\begin{align*}
   \frac{\frac23g+7}{g+14}&=\frac58 \\
   \frac{16}{3}g+56&=5g+70 \\
   \frac13g&=14 \\
   g&=\textbf{(C) } 42.
   \end{align*}$
*)

Require Import Nat.

Theorem amc12b_2020_p5 :
  forall (ap bp aw al bw bl : nat),
  ap = aw + al -> (* no draws *)
  bp = bw + bl ->
  3* aw = 2 * ap ->
  8* bw = 5 * bp ->
  aw = 7+bw ->
  al = 7+bl ->
  ap = 42.
Proof.
Admitted.
