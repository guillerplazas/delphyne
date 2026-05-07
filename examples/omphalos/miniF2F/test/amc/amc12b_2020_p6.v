(* miniF2F problem: amc12b_2020_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For all integers $n \geq 9,$ the value of
   $\frac{(n+2)!-(n+1)!}{n!}$is always which of the following?

   $\textbf{(A) } \text{a multiple of 4} \qquad \textbf{(B) } \text{a multiple of 10}
   \qquad \textbf{(C) } \text{a prime number} \qquad \textbf{(D) } \text{a perfect
   square} \qquad \textbf{(E) } \text{a perfect cube}$ Show that it is \textbf{(D) }
   \text{a perfect square}.

   Informal proof:
   We first expand the expression:
   $\frac{(n+2)!-(n+1)!}{n!} = \frac{(n+2)(n+1)n!-(n+1)n!}{n!}.$
   We can now divide out a common factor of $n!$ from each term of the numerator:
   $(n+2)(n+1)-(n+1).$
   Factoring out $(n+1),$ we get $[(n+2)-1](n+1) = (n+1)^2,$
   which proves that the answer is $\textbf{(D) } \text{a perfect square}.$
*)



Require Import Coq.Arith.Arith.
Require Import Coq.Arith.PeanoNat.

Theorem amc12b_2020_p6:
  forall (n : nat),
    9 <= n ->
    exists x : nat,
      x ^ 2 = (fact (n + 2) - fact (n + 1)) / fact n.

Proof.
Admitted.
