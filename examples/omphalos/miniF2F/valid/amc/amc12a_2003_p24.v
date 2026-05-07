(* miniF2F problem: amc12a_2003_p24
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a\geq b > 1,$ what is the largest possible value of $\log_{a}(a/b) +
   \log_{b}(b/a)?$

   $
   \mathrm{(A)}\ -2      \qquad
   \mathrm{(B)}\ 0     \qquad
   \mathrm{(C)}\ 2      \qquad
   \mathrm{(D)}\ 3      \qquad
   \mathrm{(E)}\ 4
   $ Show that it is \textbf{B}.

   Informal proof:
   Using logarithmic rules, we see that

   $\log_{a}a-\log_{a}b+\log_{b}b-\log_{b}a = 2-(\log_{a}b+\log_{b}a)$
   $=2-(\log_{a}b+\frac {1}{\log_{a}b})$

   Since $a$ and $b$ are both greater than $1$, using [[AM-GM]] gives that the term in
   parentheses must be at least $2$, so the largest possible values is $2-2=0
   \Rightarrow \textbf{B}.$

   Note that the maximum occurs when $a=b$.
*)

Require Import Coq.Reals.Reals.
Open Scope R_scope.



Theorem amc12a_2003_p24:
  forall (a b : R),
    b <= a ->
    1 < b ->
    ln(a/b) / ln(a) + ln(b/a) / ln(b) <= 0.

Proof.
Admitted.
