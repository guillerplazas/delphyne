(* miniF2F problem: amc12a_2020_p13
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   There are integers $a, b,$ and $c,$ each greater than $1,$ such that

   $\sqrt[a]{N\sqrt[b]{N\sqrt[c]{N}}} = \sqrt[36]{N^{25}}$

   for all $N \neq 1$. What is $b$?

   $\textbf{(A) } 2 \qquad \textbf{(B) } 3 \qquad \textbf{(C) } 4 \qquad \textbf{(D) } 5
   \qquad \textbf{(E) } 6$ Show that it is \textbf{(B) } 3..

   Informal proof:
   $\sqrt[a]{N\sqrt[b]{N\sqrt[c]{N}}}$ can be simplified to
   $N^{\frac{1}{a}+\frac{1}{ab}+\frac{1}{abc}}.$

   The equation is then $N^{\frac{1}{a}+\frac{1}{ab}+\frac{1}{abc}}=N^{\frac{25}{36}}$
   which implies that $\frac{1}{a}+\frac{1}{ab}+\frac{1}{abc}=\frac{25}{36}.$

   $a$ has to be $2$ since $\frac{25}{36}>\frac{7}{12}$. $\frac{7}{12}$ is the result
   when $a, b,$ and $c$ are $3, 2,$ and $2$  

   $b$ being $3$ will make the fraction $\frac{2}{3}$ which is close to $\frac{25}{36}$.
   

   Finally, with $c$ being $6$, the fraction becomes $\frac{25}{36}$. In this case $a,
   b,$ and $c$ work, which means that $b$ must equal $\textbf{(B) } 3.$
*)

Require Import Reals.
Require Import ZArith.
Open Scope R_scope.

Theorem amc12a_2020_p13 :
  forall (a b c : nat) (n : R),
    0 < n ->
    n <> 1 ->
    (1 < a)%nat /\ (1 < b)%nat /\ (1 < c)%nat ->
    Rpower (n * Rpower (n * Rpower n (/ INR c)) (/ INR b)) (/ INR a) = Rpower n (25/36) ->
    b = 3%nat.

Proof.
Admitted.
