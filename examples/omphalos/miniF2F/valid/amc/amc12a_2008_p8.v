(* miniF2F problem: amc12a_2008_p8
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the [[volume]] of a [[cube]] whose [[surface area]] is twice that of a cube
   with volume 1? 

   $\mathrm{(A)}\ \sqrt{2}\qquad\mathrm{(B)}\ 2\qquad\mathrm{(C)}\
   2\sqrt{2}\qquad\mathrm{(D)}\ 4\qquad\mathrm{(E)}\ 8$ Show that it is \mathrm{(C)}.

   Informal proof:
   A cube with volume $1$ has a side of length $\sqrt[3]{1}=1$ and thus a surface area
   of $6 \cdot 1^2=6$. 

   A cube whose surface area is $6\cdot2=12$ has a side of length
   $\sqrt{\frac{12}{6}}=\sqrt{2}$ and a volume of
   $(\sqrt{2})^3=2\sqrt{2}\Rightarrow\mathrm{(C)}$.


   Alternatively, we can use the fact that the surface area of a cube is directly
   proportional to the square of its side length. Therefore, if the surface area of a
   cube increases by a factor of $2$, its side length must increase by a factor of
   $\sqrt{2}$, meaning the new side length of the cube is $1 * \sqrt{2} = \sqrt{2}$. So,
   its volume is $({\sqrt{2}})^3 = 2\sqrt{2} \Rightarrow\mathrm{(C)}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2008_p8 :
  forall (x y : R),
  (0 < x) /\ (0 < y) -> 
  y^3 = 1 ->
  6 * x^2 = 2 * (6 * y^2) ->
  x^3 = 2 * sqrt 2.
Proof.
Admitted.