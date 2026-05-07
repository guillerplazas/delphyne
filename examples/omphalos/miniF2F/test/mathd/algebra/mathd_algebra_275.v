(* miniF2F problem: mathd_algebra_275
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $\left(\sqrt[4]{11}\right)^{3x-3}=\frac{1}{5}$, what is the value of
   $\left(\sqrt[4]{11}\right)^{6x+2}$? Express your answer as a fraction. Show that it
   is \frac{121}{25}.

   Informal proof:
   We rewrite $\left(\sqrt[4]{11}\right)^{6x+2}$ and then substitute the given equation:
   \begin{align*}
   \left(\sqrt[4]{11}\right)^{6x+2}&=\left(\sqrt[4]{11}\right)^{6x-6}\cdot
   \left(\sqrt[4]{11}\right)^{8}\\
   &=\left(\left(\sqrt[4]{11}\right)^{3x-3}\right)^2\cdot\left(11^{1/4}\right)^{8}\\
   &=\left(\frac{1}{5}\right)^2\cdot11^{(8/4)}\\
   &=\frac{1}{25}\cdot121\\
   &=\frac{121}{25}
   \end{align*}
*)

Require Import Coq.Reals.Reals.
Require Import Coquelicot.Coquelicot.

Open Scope R_scope.



Theorem mathd_algebra_275 : 
  forall x : R,
    Rpower (Rpower 11 (1/4)) (3*x - 3) = 1/5 ->
    Rpower (Rpower 11 (1/4)) (6*x + 2) = 121/25.

Proof.
Admitted.
