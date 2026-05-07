(* miniF2F problem: imo_1978_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f$ be an injective function from ${1,2,3,\ldots}$ in itself. Prove that for any
   $n$ we have: $\sum_{k=1}^{n} f(k)k^{-2} \geq \sum_{k=1}^{n} k^{-1}.$

   Informal proof:
   We know that all the unknowns are integers, so the smallest one must greater or equal
   to 1.

   Let me denote the permutations of $(k_1,k_2,...,k_n)$ with $(y_1,y_2,...,y_n)=y_i ( *
   )$.

   From the rearrangement's inequality we know that $\text{Random Sum} \geq
   \text{Reversed Sum}$.

   We will denote we permutations of $y_i$ in this form $y_n \geq ...\geq y_1$.

   So we have $\frac{k_1}{1^2}+\frac{k_2}{2^2}+...+\frac{k_n}{n^2} \geq \frac{y_1}{1^2}+
   \frac{y_2}{2^2}+...+ \frac{y_n}{n^2} \geq 1+\frac{1}{2}+...+\frac{1}{n}$.

   Let's denote $\frac{y_1}{1^2}+ \frac{y_2}{2^2}+...+ \frac{y_n}{n^2}=T$ and
   $1+\frac{1}{2}+...+\frac{1}{n}=S$.

   We have $T \geq S$. Which comes from $y_1 \geq1, y_2 \geq2, ...,y_n \geq n$.

   So we are done.

   The above solution was posted and copyrighted by Davron. The original thread for this
   problem can be found here: [https://aops.com/community/p509573]
*)

Require Import Reals.
Require Import Nat.
Require Import Lra.

Open Scope R_scope.

Theorem imo_1978_p5 :
  forall (n : nat) (f : nat -> nat),
    (forall x y, f x = f y -> x = y) ->  
    f O = O ->
    (0 < n)%nat ->
    sum_f_R0 (fun k => 1 / INR (S k)) (pred n) <= 
    sum_f_R0 (fun k => INR (f (S k)) / (INR (S k) * INR (S k))) (pred n).

Proof.
Admitted.
