(* miniF2F problem: amc12a_2002_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For how many positive integers $m$ does there exist at least one positive integer n
   such that $m \cdot n \le m + n$?

   $ \textbf{(A) } 4\qquad \textbf{(B) } 6\qquad \textbf{(C) } 9\qquad \textbf{(D) }
   12\qquad \textbf{(E) } \text{infinitely many} $ Show that it is \textbf{(E) }
   \text{infinitely many}.

   Informal proof:
   For any $m$ we can pick $n=1$, we get $m \cdot 1 \le m + 1$,
   therefore the answer is $\textbf{(E) } \text{infinitely many}$.
*)

Require Import Arith.

Theorem amc12a_2002_p6
  (n : nat)
  (h₀ : 0 < n) :
  exists m, m > n /\ exists p, m * p <= m + p.
Proof.
Admitted.