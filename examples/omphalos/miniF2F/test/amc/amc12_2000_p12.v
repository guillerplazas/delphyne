(* miniF2F problem: amc12_2000_p12
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $A, M,$ and $C$ be [[nonnegative integer]]s such that $A + M + C=12$. What is the
   maximum value of $A \cdot M \cdot C + A \cdot M + M \cdot C + A \cdot C$?

   $ \mathrm{(A) \ 62 } \qquad \mathrm{(B) \ 72 } \qquad \mathrm{(C) \ 92 } \qquad
   \mathrm{(D) \ 102 } \qquad \mathrm{(E) \ 112 }  $ Show that it is \text{E}.

   Informal proof:
   It is not hard to see that 
   $(A+1)(M+1)(C+1)=$
   $AMC+AM+AC+MC+A+M+C+1$
   Since $A+M+C=12$, we can rewrite this as
   $(A+1)(M+1)(C+1)=$
   $AMC+AM+AC+MC+13$
   So we wish to maximize
   $(A+1)(M+1)(C+1)-13$
   Which is largest when all the factors are equal (consequence of AM-GM).  Since
   $A+M+C=12$, we set $A=M=C=4$
   Which gives us 
   $(4+1)(4+1)(4+1)-13=112$
   so the answer is $\text{E}$.
   I wish you understand this problem and can use it in other problems.
*)

Theorem amc12_2000_p12 (A M C : nat) (h0 : A + M + C = 12) : 
  A * M * C + A * M + M * C + A * C <= 112.
Proof.
Admitted.