(* miniF2F problem: amc12a_2021_p22
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that the roots of the polynomial $P(x)=x^3+ax^2+bx+c$ are $\cos
   \frac{2\pi}7,\cos \frac{4\pi}7,$ and $\cos \frac{6\pi}7$, where angles are in
   radians. What is $abc$?

   $\textbf{(A) }{-}\frac{3}{49} \qquad \textbf{(B) }{-}\frac{1}{28} \qquad \textbf{(C)
   }\frac{\sqrt[3]7}{64} \qquad \textbf{(D) }\frac{1}{32}\qquad \textbf{(E)
   }\frac{1}{28}$ Show that it is \textbf{(D) }\frac{1}{32}.

   Informal proof:
   Let $z=e^{\frac{2\pi i}{7}}.$ Since $z$ is a $7$th root of unity, we have $z^7=1.$
   For all integers $k,$ note that
   $\cos\frac{2k\pi}{7}=\operatorname{Re}\left(z^k\right)=\operatorname{Re}\left(z^{-k}\right)$
   and
   $\sin\frac{2k\pi}{7}=\operatorname{Im}\left(z^k\right)=-\operatorname{Im}\left(z^{-k}\right).$
   It follows that
   $\begin{alignat*}{4}
   \cos\frac{2\pi}{7} &= \frac{z+z^{-1}}{2} &&= \frac{z+z^6}{2}, \\
   \cos\frac{4\pi}{7} &= \frac{z^2+z^{-2}}{2} &&= \frac{z^2+z^5}{2}, \\
   \cos\frac{6\pi}{7} &= \frac{z^3+z^{-3}}{2} &&= \frac{z^3+z^4}{2}.
   \end{alignat*}$
   By geometric series, we conclude that $\sum_{k=0}^{6}z^k=\frac{1-1}{1-z}=0.$
   Alternatively, recall that the $7$th roots of unity satisfy the equation $z^7-1=0.$
   By Vieta's Formulas, the sum of these seven roots is $0.$

   As a result, we get $\sum_{k=1}^{6}z^k=-1.$
   Let
   $(r,s,t)=\left(\cos{\frac{2\pi}{7}},\cos{\frac{4\pi}{7}},\cos{\frac{6\pi}{7}}\right).$
   By Vieta's Formulas, the answer is
   $\begin{align*}
   abc&=[-(r+s+t)](rs+st+tr)(-rst) \\
   &=(r+s+t)(rs+st+tr)(rst) \\
   &=\left(\frac{\sum_{k=1}^{6}z^k}{2}\right)\left(\frac{2\sum_{k=1}^{6}z^k}{4}\right)\left(\frac{1+\sum_{k=0}^{6}z^k}{8}\right)
   \\
   &=\frac{1}{32}\left(\sum_{k=1}^{6}z^k\right)\left(\sum_{k=1}^{6}z^k\right)\left(1+\sum_{k=0}^{6}z^k\right)
   \\
   &=\frac{1}{32}(-1)(-1)(1) \\
   &=\textbf{(D) }\frac{1}{32}.
   \end{align*}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12a_2021_p22:
  forall (a b c : R) (f : R -> R),
  (forall x : R, f x = x^3 + a*x^2 + b*x + c) ->
  (forall x : R, f x = 0 <-> 
    x = cos((2*PI)/7) \/ x = cos((4*PI)/7) \/ x = cos((6*PI)/7)) ->
  a * b * c = 1/32.
Proof.
Admitted.