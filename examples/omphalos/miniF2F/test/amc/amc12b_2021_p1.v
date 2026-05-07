(* miniF2F problem: amc12b_2021_p1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many integer values of $x$ satisfy $|x|<3\pi$?

   $\textbf{(A)} ~9 \qquad\textbf{(B)} ~10 \qquad\textbf{(C)} ~18 \qquad\textbf{(D)} ~19
   \qquad\textbf{(E)} Show that it is \textbf{(D)} ~19.

   Informal proof:
   Since $3\pi\approx9.42$, we multiply $9$ by $2$ for the integers from $1$ to $9$ and
   the integers from $-1$ to $-9$ and add $1$ to account for $0$ to get $\textbf{(D)}
   ~19$.
*)

Require Import Reals.
Require Import ZArith.
Require Import Finite_sets_facts.
Require Import Coquelicot.Coquelicot.

Theorem amc12b_2021_p1:
  let S := fun x:Z => (Rabs (IZR x) < 3 * PI)%R in
  cardinal Z S 19%nat.

Proof.
Admitted.
