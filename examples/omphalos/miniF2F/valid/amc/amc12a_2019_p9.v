(* miniF2F problem: amc12a_2019_p9
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A sequence of numbers is defined recursively by $a_1 = 1$, $a_2 = \frac{3}{7}$, and
   $a_n=\frac{a_{n-2} \cdot a_{n-1}}{2a_{n-2} - a_{n-1}}$for all $n \geq 3$ Then
   $a_{2019}$ can be written as $\frac{p}{q}$, where $p$ and $q$ are relatively prime
   positive integers. What is $p+q ?$

   $\textbf{(A) } 2020 \qquad\textbf{(B) } 4039 \qquad\textbf{(C) } 6057
   \qquad\textbf{(D) } 6061 \qquad\textbf{(E) } 8078$ Show that it is \textbf{(E) }8078.

   Informal proof:
   Using the recursive formula, we find $a_3=\frac{3}{11}$, $a_4=\frac{3}{15}$, and so
   on. It appears that $a_n=\frac{3}{4n-1}$, for all $n$. Setting $n=2019$, we find
   $a_{2019}=\frac{3}{8075}$, so the answer is $\textbf{(E) }8078$.

   To prove this formula, we use induction. We are given that $a_1=1$ and
   $a_2=\frac{3}{7}$, which satisfy our formula. Now assume the formula holds true for
   all $n\le m$ for some positive integer $m$. By our assumption,
   $a_{m-1}=\frac{3}{4m-5}$ and $a_m=\frac{3}{4m-1}$. Using the recursive formula,
   $a_{m+1}=\frac{a_{m-1}\cdot
   a_m}{2a_{m-1}-a_m}=\frac{\frac{3}{4m-5}\cdot\frac{3}{4m-1}}{2\cdot\frac{3}{4m-5}-\frac{3}{4m-1}}=\frac{\left(\frac{3}{4m-5}\cdot\frac{3}{4m-1}\right)(4m-5)(4m-1)}{\left(2\cdot\frac{3}{4m-5}-\frac{3}{4m-1}\right)(4m-5)(4m-1)}=\frac{9}{6(4m-1)-3(4m-5)}=\frac{3}{4(m+1)-1},$
   so our induction is complete.
*)

Require Import QArith.
Require Import Nat.

Theorem amc12a_2019_p9 :
  forall (a : nat -> Q),
    a (1%nat) = 1%Q ->
    a (2%nat) = (3#7)%Q ->
    (forall n : nat, a (S (S n)) = 
      Qdiv (Qmult (a n) (a (S n)))
           (Qminus (Qmult (2#1)%Q (a n)) (a (S n)))) ->
    Z.add (Qnum (Qred (a (2019%nat)))) (Z.pos (Qden (Qred (a (2019%nat))))) = 8078%Z.

Proof.
Admitted.
