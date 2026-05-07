(* miniF2F problem: amc12a_2008_p25
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A sequence $(a_1,b_1)$, $(a_2,b_2)$, $(a_3,b_3)$, $\ldots$ of points in the
   coordinate plane satisfies

   $(a_{n + 1}, b_{n + 1}) = (\sqrt {3}a_n - b_n, \sqrt {3}b_n + a_n)$  for $n =
   1,2,3,\ldots$.

   Suppose that $(a_{100},b_{100}) = (2,4)$.  What is $a_1 + b_1$?

   $\mathrm{(A)}\ -\frac{1}{2^{97}}\qquad\mathrm{(B)}\
   -\frac{1}{2^{99}}\qquad\mathrm{(C)}\ 0\qquad\mathrm{(D)}\
   \frac{1}{2^{98}}\qquad\mathrm{(E)}\ \frac{1}{2^{96}}$ Show that it is \mathrm{(D)}.

   Informal proof:
   This sequence can also be expressed using matrix multiplication as follows: 

   $\left[ \begin{array}{c} a_{n+1} \\ b_{n+1} \end{array} \right] = \left[
   \begin{array}{cc} \sqrt{3} & -1 \\ 1 & \sqrt{3} \end{array} \right] \left[
   \begin{array}{c} a_{n} \\ b_{n} \end{array} \right] = 2 \left[ \begin{array}{cc} \cos
   30^\circ & -\sin 30^\circ \\ \sin 30^\circ & \ \cos 30^\circ \end{array} \right]
   \left[ \begin{array}{c} a_{n} \\ b_{n} \end{array} \right]$. 

   Thus, $(a_{n+1} , b_{n+1})$ is formed by rotating $(a_n , b_n)$ counter-clockwise
   about the origin by $30^\circ$ and dilating the point's position with respect to the
   origin by a factor of $2$. 

   So, starting with $(a_{100},b_{100})$ and performing the above operations $99$ times
   in reverse yields $(a_1,b_1)$. 

   Rotating $(2,4)$ clockwise by $99 \cdot 30^\circ \equiv 90^\circ$ yields $(4,-2)$. A
   dilation by a factor of $\frac{1}{2^{99}}$ yields the point $(a_1,b_1) =
   \left(\frac{4}{2^{99}}, -\frac{2}{2^{99}} \right) = \left(\frac{1}{2^{97}},
   -\frac{1}{2^{98}} \right)$. 

   Therefore, $a_1 + b_1 = \frac{1}{2^{97}} - \frac{1}{2^{98}} = \frac{1}{2^{98}}
   \Rightarrow D$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem amc12a_2008_p25 :
  forall (a b : nat -> R),
  (forall n, a (S n) = (sqrt (IZR 3)) * (a n) - (b n)) ->
  (forall n, b (S n) = (sqrt (IZR 3)) * (b n) + (a n)) ->
  a (100%nat) = 2%R ->
  b (100%nat) = 4%R ->
  a 1%nat + b 1%nat = 1 / (2^98)%R.

Proof.
Admitted.
