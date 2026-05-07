(* miniF2F problem: amc12a_2020_p15
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   In the complex plane, let $A$ be the set of solutions to $z^{3}-8=0$ and let $B$ be
   the set of solutions to $z^{3}-8z^{2}-8z+64=0.$ What is the greatest distance between
   a point of $A$ and a point of $B?$

   $\textbf{(A) } 2\sqrt{3} \qquad \textbf{(B) } 6 \qquad \textbf{(C) } 9 \qquad
   \textbf{(D) } 2\sqrt{21} \qquad \textbf{(E) } 9+\sqrt{3}$ Show that it is \textbf{(D)
   } 2\sqrt{21}.

   Informal proof:
   We solve each equation separately:
   <ol style=''margin-left: 1.5em;''>
   <li>We solve $z^{3}-8=0$ by De Moivre's Theorem.<p>
   Let $z=r(\cos\theta+i\sin\theta)=r\operatorname{cis}\theta,$ where $r$ is the
   magnitude of $z$ such that $r\geq0,$ and $\theta$ is the argument of $z$ such that
   $0\leq\theta<2\pi.$ <p>
   We have $z^3=r^3\operatorname{cis}(3\theta)=8(1),$ from which
   <ul style=''list-style-type:square;''>
   <li>$r^3=8,$ so $r=2.$</li><p>
   <li>$\begin{cases}
   \begin{aligned}
   \cos(3\theta) &= 1 \\
   \sin(3\theta) &= 0
   \end{aligned},
   \end{cases}$ so $3\theta=0,2\pi,4\pi,$ or $\theta=0,\frac{2\pi}{3},\frac{4\pi}{3}.$
   </li><p>
   </ul>
   The set of solutions to $z^{3}-8=0$ is
   $\boldsymbol{A=\left\{2,-1+\sqrt{3}i,-1-\sqrt{3}i\right\}}.$ In the complex plane,
   the solutions form the vertices of an equilateral triangle whose circumcircle has
   center $0$ and radius $2.$</li><p>
   <li>We solve $z^{3}-8z^{2}-8z+64=0$ by factoring by grouping.</li><p>
   We have
   $\begin{align*}
   z^2(z-8)-8(z-8)&=0 \\
   \bigl(z^2-8\bigr)(z-8)&=0.
   \end{align*}$
   The set of solutions to $z^{3}-8z^{2}-8z+64=0$ is
   $\boldsymbol{B=\left\{2\sqrt{2},-2\sqrt{2},8\right\}}.$
   </ol>
   In the graph below, the points in set $A$ are shown in red, and the points in set $B$
   are shown in blue. The greatest distance between a point of $A$ and a point of $B$ is
   the distance between $-1\pm\sqrt{3}i$ to $8,$ as shown in the dashed line segments.

   By the Distance Formula, the answer is
   $\sqrt{(-1-8)^2+\left(\pm\sqrt{3}-0\right)^2}=\sqrt{84}=\textbf{(D) } 2\sqrt{21}.$
   ~lopkiloinm
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Theorem amc12a_2020_p15 :
  forall (a b : C),
    (a^3 - 8 = 0)%C ->
    (b^3 - 8 * b^2 - 8 * b + 64 = 0)%C ->
    Cmod (a - b) <= 2 * sqrt 21.
Proof.
Admitted.
