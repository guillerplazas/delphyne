(* miniF2F problem: mathd_algebra_17
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Solve for $a$: $$\sqrt{4+\sqrt{16+16a}}+ \sqrt{1+\sqrt{1+a}} = 6.$$ Show that it is
   8.

   Informal proof:
   We can factor a constant out of the first radical:
   \begin{align*}
   \sqrt{4+\sqrt{16+16a}} &= \sqrt{4+\sqrt{16(1+a)}}\\
   &= \sqrt{4+4\sqrt{1+a}}\\
   &= \sqrt{4(1+\sqrt{1+a})}\\
   &= 2\sqrt{1+\sqrt{1+a}}
   \end{align*}Then, we can combine like terms and solve:

   \begin{align*}
   2\sqrt{1+\sqrt{1+a}}+ \sqrt{1+\sqrt{1+a}} &= 6\\
   \Rightarrow 3\sqrt{1+\sqrt{1+a}} &= 6\\
   \Rightarrow \sqrt{1+\sqrt{1+a}} &= 2\\
   \Rightarrow 1+\sqrt{1+a} &= 4\\
   \Rightarrow \sqrt{1+a} &= 3\\
   \Rightarrow 1+a &= 9\\
   \Rightarrow a &= 8
   \end{align*}
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_17 (a : R) 
  (h : sqrt (4 + sqrt (16 + 16 * a)) + sqrt (1 + sqrt (1 + a)) = 6) :
  a = 8.
Proof.
Admitted.