(* miniF2F problem: amc12a_2009_p15
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For what value of $n$ is $i + 2i^2 + 3i^3 + \cdots + ni^n = 48 + 49i$?

   Note: here $i = \sqrt { - 1}$.

   $\textbf{(A)}\ 24 \qquad \textbf{(B)}\ 48 \qquad \textbf{(C)}\ 49 \qquad
   \textbf{(D)}\ 97 \qquad \textbf{(E)}\ 98$ Show that it is \mathbf{D}.

   Informal proof:
   We know that $i^x$ cycles every $4$ powers so we group the sum in $4$s. 
   $i+2i^2+3i^3+4i^4=2-2i$
   $5i^5+6i^6+7i^7+8i^8=2-2i$

   We can postulate that every group of $4$ is equal to $2-2i$.
   For 24 groups we thus, get $48-48i$ as our sum. 
   We know the solution must lie near
   The next term is the $24*4+1=97$th term. This term is equal to $97i$ (first in a
   group of $4$ so $i^{97}=i$) and our sum is now $48+49i$ so
   $n=97\Rightarrow\mathbf{D}$ is our answer
*)

Require Import List.
Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem amc12a_2009_p15 :
  forall (n : nat), (0 < n)%nat ->
  fold_left Cplus (map (fun k => INR k * Ci ^ k) (seq 1 n)) 0
    = 48 + 49 * Ci ->
  (n = 97)%nat.
Proof.
Admitted.
