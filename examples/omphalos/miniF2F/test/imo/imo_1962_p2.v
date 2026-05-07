(* miniF2F problem: imo_1962_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Determine all real numbers $x$ which satisfy the inequality:

   <center>
   $\sqrt{\sqrt{3-x}-\sqrt{x+1}}>\dfrac{1}{2}$
   </center> Show that it is \left[ ~ -1,\quad 1-\dfrac{\sqrt{127}}{32} ~ \right).

   Informal proof:
   Obviously we need $\sqrt{3-x} \geq \sqrt{x+1}$ for the outer square root to be
   defined, $x\leq 3$ for the first inner square root to be defined,
   and $x\geq -1$ for the second inner square root to be defined. Solving these we get
   that the left hand side is defined for $x\in \left[ -1,1 \right]$.

   Now obviously the function $f(x)=\sqrt{\sqrt{3-x}-\sqrt{x+1}}$ is continuous on
   $\left[ -1,1 \right]$, with $f(-1)=\sqrt 2$ and $f(1)=0$.
   Moreover, as $3-x$ is a decreasing and $x+1$ an increasing function, both
   $\sqrt{3-x}$ and $-\sqrt{x+1}$ are decreasing functions, and hence $f(x)$ is a
   decreasing function. Therefore there is exactly one solution to $f(x)=\dfrac{1}{2}$.

   We can now find this solution:

   $
   \begin{align*}
   \sqrt{\sqrt{3-x}-\sqrt{x+1}} &= \dfrac{1}{2}
   \\
   \sqrt{3-x}-\sqrt{x+1} &= \dfrac{1}{4}
   \\
   \sqrt{3-x} &= \dfrac{1}{4} + \sqrt{x+1}
   \\
   3-x &= \dfrac 1{16} + x+1 + \dfrac{\sqrt{x+1}}2
   \\
   2 - 2x - \dfrac 1{16} &= \dfrac{\sqrt{x+1}}2
   \\
   31 - 32x &= 8\sqrt{x+1}
   \\
   1024 x^2 - 1984x + 961 &= 64(x+1)
   \\
   1024 x^2 - 2048x + 897 &= 0
   \end{align*}
   $

   (Note the little trick in the third row: placing the square roots on opposite sides
   of the equation. Squaring the equation in the second row would work as well, but this
   way is a little more pleasant, as the one remaining square root after the squaring
   will essentially be one of the original two, not their product.)

   Solving the quadratic equation for $x$, we get
   $
   x_{1,2}=\dfrac{ 2^{11} \pm \sqrt{ 2^{22} - 2^{12}\cdot 897} }{2^{11}} = 1 \pm
   \dfrac{\sqrt{127}}{32}
   $

   The reason why we got two roots is that while solving the original equation we
   squared both sides twice, and this could have created additional solutions. In this
   case, obviously the root that is larger than $1$ is the additional solution, and
   $x=1-\dfrac{\sqrt{127}}{32}$ is the root we need.

   Hence the solutions to the given inequality are precisely the reals in the interval
   $\left[ ~ -1,\quad 1-\dfrac{\sqrt{127}}{32} ~ \right)$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1962_p2 :
  forall x : R,
  0 <= 3 - x ->
  0 <= x + 1 ->
  1/2 < sqrt (sqrt (3 - x) - sqrt (x + 1)) ->
  -1 <= x /\ x < 1 - sqrt 127 / 32.

Proof.
Admitted.
