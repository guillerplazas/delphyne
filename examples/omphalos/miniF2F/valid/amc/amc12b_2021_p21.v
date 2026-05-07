(* miniF2F problem: amc12b_2021_p21
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $S$ be the sum of all positive real numbers $x$ for
   which$x^{2^{\sqrt2}}=\sqrt2^{2^x}.$Which of the following statements is true?

   $\textbf{(A) }S<\sqrt2 \qquad \textbf{(B) }S=\sqrt2 \qquad \textbf{(C)
   }\sqrt2<S<2\qquad \textbf{(D) }2\le S<6 \qquad \textbf{(E) }S\ge 6$ Show that it is
   \textbf{(D) }2\le S<6.

   Informal proof:
   Note that
   $\begin{align*}
   x^{2^{\sqrt{2}}} &= {\sqrt{2}}^{2^x} \\
   2^{\sqrt{2}} \log_2 x &= 2^{x} \log_2 \sqrt{2}.
   \end{align*}$
   (At this point we see by inspection that $x=\sqrt{2}$ is a solution.)

   We simplify the RHS, then take the base-$2$ logarithm for both sides:
   $\begin{align*}
   2^{\sqrt{2}} \log_2 x &= 2^{x-1} \\
   \log_2{\left(2^{\sqrt{2}} \log_2 x\right)} &= x-1 \\
   \sqrt{2} + \log_2 \log_2 x &= x-1 \\
   \log_2 \log_2 x &= x - 1 - \sqrt{2}.
   \end{align*}$
   The RHS is a line; the LHS is a concave curve that looks like a logarithm and has $x$
   intercept at $(2,0).$

   There are at most two solutions, one of which is $\sqrt{2}.$ But note that at $x=2,$
   we have $\log_2 \log_2 {2} = 0 > 2 - 1 - \sqrt{2},$ meaning that the log log curve is
   above the line, so it must intersect the line again at a point $x > 2.$ Now we check
   $x=4$ and see that $\log_2 \log_2 {4} = 1 < 4 - 1 - \sqrt{2},$ which means at $x=4$
   the line is already above the log log curve. Thus, the second solution lies in the
   interval $(2,4).$
   The answer is $\textbf{(D) }2\le S<6.$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import List.

Open Scope R_scope.

Theorem amc12b_2021_p21 (S : list R) :
  NoDup S ->
  (forall x : R, In x S <-> 
    (0 < x /\ Rpower x (Rpower 2 (sqrt 2)) = Rpower (sqrt 2) (Rpower 2 x))) ->
  2 <= fold_right Rplus 0 S /\ fold_right Rplus 0 S < 6.

Proof.
Admitted.
