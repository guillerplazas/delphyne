(* miniF2F problem: mathd_algebra_422
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $f(x)=5x-12$, find a value for $x$ so that $f^{-1}(x)=f(x+1)$. Show that it is
   \frac{47}{24}.

   Informal proof:
   Substituting $f^{-1}(x)$ into our expression for $f$, we get
   \[f(f^{-1}(x))=5f^{-1}(x)-12.\]Since $f(f^{-1}(x))=x$ for all $x$ in the domain of
   $f^{-1}$, we have \[x=5f^{-1}(x)-12.\]Solving for $f^{-1}(x)$ gives
   \[f^{-1}(x)=\frac{x+12}5.\]The equation $f^{-1}(x)=f(x+1)$ now reads
   \[\frac{x+12}5=5(x+1)-12=5x-7.\]Cross-multiplication gives \[x+12=25x-35.\]Isolating
   $x$ gives us  \[24x=47.\]Solving for $x$, we find $x = \frac{47}{24}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem mathd_algebra_422 :
  forall (x : R) (sigma : R -> R),
    (forall x, sigma x = 5 * x - 12) ->
    exists sigma_inv : R -> R,
      (forall x, sigma_inv x = (x + 12) / 5) ->
      sigma (x + 1) = sigma_inv x ->
      x = 47 / 24.
Proof.
Admitted.