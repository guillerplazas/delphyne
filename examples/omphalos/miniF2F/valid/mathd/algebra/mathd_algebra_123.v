(* miniF2F problem: mathd_algebra_123
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Together, Amy and Betty have 20 apples. Amy has three times the number of apples that
   Betty has. How many more apples than Betty does Amy have? Show that it is 10.

   Informal proof:
   Call the amount of apples Amy has $a$ and the amount of apples Betty has $b$. We can
   use the following system of equations to represent the given information:
   \begin{align*}
   a + b &= 20 \\
   a &= 3b \\
   \end{align*}Substituting for $a$ into the first equation gives $3b + b = 20$. Solving
   for $b$ gives $b = 5$. Thus $a = 15$. So Amy has $15 - 5 = 10$ more apples than
   Betty.
*)

Require Import Arith.

Theorem mathd_algebra_123
  (a b : nat)
  (h₀ : a + b = 20)
  (h₁ : a = 3 * b) :
  a - b = 10.
Proof.
Admitted.