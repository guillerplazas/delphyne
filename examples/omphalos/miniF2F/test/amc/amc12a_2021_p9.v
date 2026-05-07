(* miniF2F problem: amc12a_2021_p9
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Which of the following is equivalent to
   $(2+3)(2^2+3^2)(2^4+3^4)(2^8+3^8)(2^{16}+3^{16})(2^{32}+3^{32})(2^{64}+3^{64})?$
   $\textbf{(A)} ~3^{127} + 2^{127} \qquad\textbf{(B)} ~3^{127} + 2^{127} + 2 \cdot
   3^{63} + 3 \cdot 2^{63} \qquad\textbf{(C)} ~3^{128}-2^{128} \qquad\textbf{(D)}
   ~3^{128} + 2^{128} \qquad\textbf{(E)} Show that it is \textbf{(C)} ~3^{128}-2^{128}.

   Informal proof:
   By multiplying the entire equation by $3-2=1$, all the terms will simplify by
   difference of squares, and the final answer is $\textbf{(C)} ~3^{128}-2^{128}$.

   Additionally, we could also multiply the entire equation (we can let it be equal to
   $x$) by $2-3=-1$. The terms again simplify by difference of squares. This time, we
   get $-x=2^{128}-3^{128} \Rightarrow x=3^{128}-2^{128}$. Both solutions yield the same
   answer.
*)

Require Import Coq.Arith.PeanoNat.
Require Import Coq.Lists.List.
Require Import Coq.Numbers.Natural.Abstract.NDiv.

Theorem amc12a_2021_p9 :
  fold_left Nat.mul 
    (map (fun k => (2^(2^k) + 3^(2^k))) (seq 0 7)) 1 = 
  3^128 - 2^128.
Proof.
Admitted.