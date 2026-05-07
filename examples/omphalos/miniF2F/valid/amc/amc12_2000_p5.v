(* miniF2F problem: amc12_2000_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $|x - 2| = p$, where $x < 2$, then $x - p =$

   $ \textbf{(A)} \ -2 \qquad \textbf{(B)} \ 2 \qquad \textbf{(C)} \ 2-2p \qquad
   \textbf{(D)} \ 2p-2 \qquad \textbf{(E)} \ |2p-2|  $ Show that it is \text{(C)2-2p}.

   Informal proof:
   When $x < 2,$ $x-2$ is negative so $|x - 2| = 2-x = p$ and $x = 2-p$.

   Thus $x-p = (2-p)-p = 2-2p$.
   $\text{(C)2-2p}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12_2000_p5:
  forall (x p : R),
  x < 2 ->
  Rabs (x - 2) = p ->
  x - p = 2 - 2 * p.
Proof.
Admitted.