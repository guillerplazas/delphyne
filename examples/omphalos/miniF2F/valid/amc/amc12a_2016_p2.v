(* miniF2F problem: amc12a_2016_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For what value of $x$ does $10^{x}\cdot 100^{2x}=1000^{5}$?

   $\textbf{(A)}\ 1 \qquad\textbf{(B)}\ 2\qquad\textbf{(C)}\ 3\qquad\textbf{(D)}\
   4\qquad\textbf{(E)}\ 5$ Show that it is \textbf{(C)}\;3.

   Informal proof:
   We can rewrite $10^{x}\cdot 100^{2x}=1000^{5}$ as $10^{5x}=10^{15}$:
   $\begin{split}
   10^x\cdot100^{2x} & =10^x\cdot(10^2)^{2x} \\
   10^x\cdot10^{4x} & =(10^3)^5 \\
   10^{5x} & =10^{15}
   \end{split}$
   Since the bases are equal, we can set the exponents equal, giving us $5x=15$. Solving
   the equation gives us $x = \textbf{(C)}\;3.$
*)

Require Import Coq.Arith.PeanoNat.

Theorem amc12a_2016_p2 :
  forall x : nat,
    10 ^ x * 100 ^ (2 * x) = 1000 ^ 5 ->
    x = 3.

Proof.
Admitted.
