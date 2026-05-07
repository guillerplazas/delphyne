(* miniF2F problem: mathd_algebra_188
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose $f(x)$ is an invertible function, and suppose that $f(2)=f^{-1}(2)=4$.

   What is the value of $f(f(2))$? Show that it is 2.

   Informal proof:
   Since $f(2)=f^{-1}(2)$, we can substitute $f^{-1}(2)$ freely for $f(2)$. Therefore,
   $f(f(2)) = f(f^{-1}(2))$, which is $2$ (since $f(f^{-1}(x))=x$ by definition).

   Notice that we didn't actually need the value $4$ given in the problem.
*)

Require Import Reals.

Open Scope R_scope.

Theorem mathd_algebra_188
  (sigma : R -> R)
  (inv_sigma : R -> R)
  (H_bij : forall x : R, sigma (inv_sigma x) = x /\ inv_sigma (sigma x) = x)
  (H1 : sigma 2 = 4)
  (H2 : inv_sigma 2 = 4) :
  sigma (sigma 2) = 2.

Proof.
Admitted.
