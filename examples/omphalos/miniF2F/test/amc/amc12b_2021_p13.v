(* miniF2F problem: amc12b_2021_p13
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many values of $\theta$ in the interval $0<\theta\le 2\pi$
   satisfy$1-3\sin\theta+5\cos3\theta = 0?$$\textbf{(A) }2 \qquad \textbf{(B) }4 \qquad
   \textbf{(C) }5\qquad \textbf{(D) }6 \qquad \textbf{(E) }8$ Show that it is
   \textbf{(D) }6.

   Informal proof:
   We rearrange to get $5\cos3\theta = 3\sin\theta-1.$
   We can graph two functions in this case: $y=5\cos{3x}$ and $y=3\sin{x} -1 $.
   Using transformation of functions, we know that $5\cos{3x}$ is just a cosine function
   with amplitude $5$ and period $\frac{2\pi}{3}$. Similarly, $3\sin{x} -1 $ is just a
   sine function with amplitude $3$ and shifted $1$ unit downward:

   So, we have $\textbf{(D) }6$ solutions.
*)

Require Import Reals.
Require Import Sets.Ensembles.
Require Import Sets.Finite_sets_facts.
Open Scope R_scope.

Theorem amc12b_2021_p13 :
  exists (S : Ensemble R), 
  (forall x : R, In R S x <-> 
    (0 < x /\ x <= 2 * PI /\ 1 - 3 * sin x + 5 * cos (3 * x) = 0)) /\
  cardinal R S 6.

Proof.
Admitted.
