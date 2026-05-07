(* miniF2F problem: amc12_2001_p21
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Four positive integers $a$, $b$, $c$, and $d$ have a product of $8!$ and satisfy:

   $
   \begin{align*}
   ab + a + b & = 524
   \\ 
   bc + b + c & = 146
   \\ 
   cd + c + d & = 104
   \end{align*}
   $

   What is $a-d$?

   $
   \text{(A) }4
   \qquad
   \text{(B) }6
   \qquad
   \text{(C) }8
   \qquad
   \text{(D) }10
   \qquad
   \text{(E) }12
   $ Show that it is 10.

   Informal proof:
   Using Simon's Favorite Factoring Trick, we can rewrite the three equations as
   follows:

   $
   \begin{align*}
   (a+1)(b+1) & = 525
   \\ 
   (b+1)(c+1) & = 147
   \\ 
   (c+1)(d+1) & = 105
   \end{align*}
   $

   Let $(e,f,g,h)=(a+1,b+1,c+1,d+1)$. We get:

   $
   \begin{align*}
   ef & = 3\cdot 5\cdot 5\cdot 7
   \\ 
   fg & = 3\cdot 7\cdot 7
   \\ 
   gh & = 3\cdot 5\cdot 7
   \end{align*}
   $

   Clearly $7^2$ divides $fg$. On the other hand, $7^2$ can not divide $f$, as it then
   would divide $ef$. Similarly, $7^2$ can not divide $g$. Hence $7$ divides both $f$
   and $g$. This leaves us with only two cases: $(f,g)=(7,21)$ and $(f,g)=(21,7)$.

   The first case solves to $(e,f,g,h)=(75,7,21,5)$, which gives us
   $(a,b,c,d)=(74,6,20,4)$, but then $abcd \not= 8!$. We do not need to multiply, it is
   enough to note e.g. that the left hand side is not divisible by $7$. (Also, a - d
   equals $70$ in this case, which is way too large to fit the answer choices.)

   The second case solves to $(e,f,g,h)=(25,21,7,15)$, which gives us a valid quadruple
   $(a,b,c,d)=(24,20,6,14)$, and we have $a-d=24-14 =10$.
*)

Require Import ZArith.
Require Import Lia.

Theorem amc12_2001_p21 :
  forall (a b c d : nat),
  a * b * c * d = fact 8 ->
  a * b + a + b = 524 ->
  b * c + b + c = 146 ->
  c * d + c + d = 104 ->
  Z.sub (Z.of_nat a) (Z.of_nat d) = 10%Z.

Proof.
Admitted.
