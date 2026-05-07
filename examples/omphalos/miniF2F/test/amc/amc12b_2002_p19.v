(* miniF2F problem: amc12b_2002_p19
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $a,b,$ and $c$ are positive [[real number]]s such that $a(b+c) = 152, b(c+a) =
   162,$ and $c(a+b) = 170$, then $abc$ is

   $\mathrm{(A)}\ 672
   \qquad\mathrm{(B)}\ 688
   \qquad\mathrm{(C)}\ 704
   \qquad\mathrm{(D)}\ 720
   \qquad\mathrm{(E)}\ 750$ Show that it is 720.

   Informal proof:
   Adding up the three equations gives $2(ab + bc + ca) = 152 + 162 + 170 = 484
   \Longrightarrow ab + bc + ca = 242$. Subtracting each of the above equations from
   this yields, respectively, $bc = 90, ca = 80, ab = 72$. Taking their product, $ab
   \cdot bc \cdot ca = a^2b^2c^2 = 90 \cdot 80 \cdot 72 = 720^2 \Longrightarrow abc =
   720 \Rightarrow \mathrm{(D)}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2002_p19 :
  forall (a b c : R),
    0 < a -> 0 < b -> 0 < c ->
    a * (b + c) = 152 -> 
    b * (c + a) = 162 ->
    c * (a + b) = 170 ->
    a * b * c = 720.
Proof.
Admitted.