(* miniF2F problem: amc12a_2021_p19
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many solutions does the equation $\sin \left( \frac{\pi}2 \cos x\right)=\cos
   \left( \frac{\pi}2 \sin x\right)$ have in the closed interval $[0,\pi]$?

   $\textbf{(A) }0 \qquad \textbf{(B) }1 \qquad \textbf{(C) }2 \qquad \textbf{(D)
   }3\qquad \textbf{(E) }4$ Show that it is \textbf{(C) }2.

   Informal proof:
   The ranges of $\frac{\pi}2 \sin x$ and $\frac{\pi}2 \cos x$ are both
   $\left[-\frac{\pi}2, \frac{\pi}2 \right],$ which is included in the range of
   $\arcsin,$ so we can use it with no issues.
   $\begin{align*}
   \frac{\pi}2 \cos x &= \arcsin \left( \cos \left( \frac{\pi}2 \sin x\right)\right) \\
   \frac{\pi}2 \cos x &= \arcsin \left( \sin \left( \frac{\pi}2 - \frac{\pi}2 \sin
   x\right)\right) \\
   \frac{\pi}2 \cos x &= \frac{\pi}2 - \frac{\pi}2 \sin x \\
   \cos x &= 1 - \sin x \\
   \cos x + \sin x &= 1.
   \end{align*}$
   This only happens at $x = 0, \frac{\pi}2$ on the interval $[0,\pi],$ because one of
   $\sin$ and $\cos$ must be $1$ and the other $0.$ Therefore, the answer is
   $\textbf{(C) }2.$
*)

Require Import Reals.
Require Import FunctionalExtensionality.
Require Import RIneq.
Require Import Classical_Pred_Type.
Require Import ClassicalEpsilon.

Open Scope R_scope.

Theorem amc12a_2021_p19 :
  exists S : R -> Prop,
  (forall x, S x <-> (0 <= x /\ x <= PI /\ 
    sin (PI/2 * cos x) = cos (PI/2 * sin x))) /\
  exists x1 x2, 
    x1 <> x2 /\
    S x1 /\ S x2 /\
    forall x, S x -> (x = x1 \/ x = x2).

Proof.
Admitted.
