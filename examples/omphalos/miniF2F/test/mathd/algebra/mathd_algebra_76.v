(* miniF2F problem: mathd_algebra_76
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For integers $n$, let \[f(n) = \left\{
   \begin{array}{cl}
   n^2 & \text{ if }n\text{ is odd}, \\
   n^2 - 4n - 1 & \text{ if }n\text{ is even}.
   \end{array}
   \right.\]Find $f(f(f(f(f(4)))))$. Show that it is 1.

   Informal proof:
   Working from the inside out, we first compute $f(4) = 4^2-4(4)-1=-1$.  Next we find
   $f(-1)=(-1)^2=1$, and then $f(1)=1^2=1$. Putting these together, we have
   $f(f(f(f(f(4)))))=f(f(f(f(-1))))=f(f(f(1)))=f(f(1))=f(1)=1$.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_algebra_76 :
  forall f : Z -> Z,
  (forall n, Z.odd n = true -> f n = n * n) ->
  (forall n, Z.even n = true -> f n = n * n - 4 * n - 1) ->
  f 4 = -1.
Proof.
Admitted.