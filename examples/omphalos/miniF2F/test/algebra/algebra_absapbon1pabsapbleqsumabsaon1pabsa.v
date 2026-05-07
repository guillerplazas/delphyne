(* miniF2F problem: algebra_absapbon1pabsapbleqsumabsaon1pabsa
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real numbers $a$ and $b$, $\frac{|a+b|}{1+|a+b|}\leq
   \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|}$.

   Informal proof:
   The LHS is equal to $1 - \frac{1}{1+|a+b|}$. Hence it suffices to prove $1\leq
   \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|} + \frac{1}{1+|a+b|}$.
   Because $|a|+|b|\geq |a+b|$, we have the RHS to satisfy

   \begin{align}
   \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|} + \frac{1}{1+|a+b|} & \geq
   \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|} + \frac{1}{1+|a|+|b|}\\
   & \geq \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|} + \frac{1}{1+|a|+|b|+|a||b|}\\
   & = \frac{|a|}{1+|a|}+\frac{|b|}{1+|b|} + \frac{1}{(1+|a|)(1+|b|)}\\
   & = \frac{|a|(1+|b|)+|b|(1+|a|)+1}{(1+|a|)(1+|b|)}\\
   & = \frac{|a|+|b|+1+2|a||b|}{(1+|a|)(1+|b|)}\\
   & \geq \frac{(1+|a|)(1+|b|)}{(1+|a|)(1+|b|)}\\
   & = 1.
   \end{align}

   Therefore the inequality holds.
*)

Require Import Reals.
Open Scope R_scope.

Theorem algebra_absapbon1pabsapbleqsumabsaon1pabsa :
  forall (a b : R),
  Rabs (a + b) / (1 + Rabs (a + b)) <= Rabs a / (1 + Rabs a) + Rabs b / (1 + Rabs b).
Proof.
Admitted.