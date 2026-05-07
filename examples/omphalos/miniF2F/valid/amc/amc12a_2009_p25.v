(* miniF2F problem: amc12a_2009_p25
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The first two terms of a sequence are $a_1 = 1$ and $a_2 = \frac {1}{\sqrt3}$. For
   $n\ge1$,

   <center>$a_{n + 2} = \frac {a_n + a_{n + 1}}{1 - a_na_{n + 1}}.$</center>

   What is $|a_{2009}|$?

   $\textbf{(A)}\ 0\qquad \textbf{(B)}\ 2 - \sqrt3\qquad \textbf{(C)}\ \frac
   {1}{\sqrt3}\qquad \textbf{(D)}\ 1\qquad \textbf{(E)}\ 2 + \sqrt3$ Show that it is
   \textbf{(A)}\ 0.

   Informal proof:
   Consider another sequence $\{\theta_1, \theta_2, \theta_3...\}$ such that $a_n =
   \tan{\theta_n}$, and $0 \leq \theta_n < 180$.

   The given recurrence becomes

   <center>$\begin{align*} a_{n + 2} & = \frac {a_n + a_{n + 1}}{1 - a_na_{n + 1}} \\
   \tan{\theta_{n + 2}} & = \frac {\tan{\theta_n} + \tan{\theta_{n + 1}}}{1 -
   \tan{\theta_n}\tan{\theta_{n + 1}}} \\
   \tan{\theta_{n + 2}} & = \tan(\theta_{n + 1} + \theta_n) \end{align*}$</center>

   It follows that $\theta_{n + 2} \equiv \theta_{n + 1} + \theta_{n} \pmod{180}$. Since
   $\theta_1 = 45, \theta_2 = 30$, all terms in the sequence $\{\theta_1, \theta_2,
   \theta_3...\}$ will be a multiple of $15$.

   Now consider another sequence $\{b_1, b_2, b_3...\}$ such that $b_n = \theta_n/15$,
   and $0 \leq b_n < 12$. The sequence $b_n$ satisfies $b_1 = 3, b_2 = 2, b_{n + 2}
   \equiv b_{n + 1} + b_n \pmod{12}$.

   As the number of possible consecutive two terms is finite, we know that the sequence
   $b_n$ is periodic. Write out the first few terms of the sequence until it starts to
   repeat.

   $\{b_n\} = \{3,2,5,7,0,7,7,2,9,11,8,7,3,10,1,11,0,11,11,10,9,7,4,11,3,2,5,7,...\}$

   Note that $b_{25} = b_1 = 3$ and $b_{26} = b_2 = 2$. Thus $\{b_n\}$ has a period of
   $24$: $b_{n + 24} = b_n$.

   It follows that $b_{2009} = b_{17} = 0$ and $\theta_{2009} = 15 b_{2009} = 0$. Thus
   $a_{2009} = \tan{\theta_{2009}} = \tan{0} = 0.$

   Our answer is $|a_{2009}| = \textbf{(A)}\ 0$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2009_p25 :
  forall (a : nat -> R),
    (a 1%nat = 1) ->
    (a 2%nat = 1/sqrt 3) ->
    (forall n : nat, (1 <= n)%nat -> 
      a (S (S n))%nat = (a n + a (S n))/(1 - a n * a (S n))) ->
    Rabs (a 2009%nat) = 0.

Proof.
Admitted.
