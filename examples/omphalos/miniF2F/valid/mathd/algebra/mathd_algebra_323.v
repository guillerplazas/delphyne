(* miniF2F problem: mathd_algebra_323
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x)=x^3-8$, what is $f^{-1}(f(f^{-1}(19)))$? Show that it is 3.

   Informal proof:
   First, by definition of the inverse of a function, $f(f^{-1}(19)) = 19$, so
   $f^{-1}(f(f^{-1}(19))) = f^{-1}(19)$.

   We then find the inverse of $f(x)$. Substituting $f^{-1}(x)$ into the expression for
   $f$, and noting that $f(f^{-1}(x)) = x$ for all $x$ in the domain of $f^{-1}$, we get
   that  \[x = (f^{-1}(x))^3 - 8.\]Solving this equation for $f^{-1}(x)$, we get that
   $f^{-1}(x)=\sqrt[3]{x+8}$. Then $f^{-1}(19) = \sqrt[3]{19+8} = \sqrt[3]{27}= 3$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_323:
  forall (sigma sigma_inv : R -> R),
    
    (forall x, sigma x = x ^ 3 - 8) ->
    
    (forall x, sigma_inv (sigma x) = x) ->
    (forall x, sigma (sigma_inv x) = x) ->
    
    sigma_inv (sigma (sigma_inv 19)) = 3.

Proof.
Admitted.
