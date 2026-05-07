(* miniF2F problem: amc12a_2009_p9
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $f(x+3)=3x^2 + 7x + 4$ and $f(x)=ax^2 + bx + c$. What is $a+b+c$?

   $\textbf{(A)}\ -1 \qquad \textbf{(B)}\ 0 \qquad \textbf{(C)}\ 1 \qquad \textbf{(D)}\
   2 \qquad \textbf{(E)}\ 3$ Show that it is 2.

   Informal proof:
   As $f(x)=ax^2 + bx + c$, we have $f(1)=a\cdot 1^2 + b\cdot 1 + c = a+b+c$. 

   To compute $f(1)$, set $x=-2$ in the first formula. We get $f(1) = f(-2+3) = 3(-2)^2
   + 7(-2) + 4 = 12 - 14 + 4 = 2$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2009_p9 :
  forall (a b c : R) (f : R -> R),
    (forall x, f (x + 3) = 3 * x^2 + 7 * x + 4) ->
    (forall x, f x = a * x^2 + b * x + c) ->
    a + b + c = 2.
Proof.
Admitted.