(* miniF2F problem: aime_1984_p7
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The [[function]] f is defined on the [[set]] of [[integer]]s and satisfies
   $f(n)=\begin{cases}
   n-3&\mbox{if}\ n\ge 1000\\
   f(f(n+5))&\mbox{if}\ n<1000\end{cases}$

   Find $f(84)$. Show that it is 997.

   Informal proof:
   Define $f^{h} = f(f(\cdots f(f(x))\cdots))$, where the function $f$ is performed $h$
   times. We find that $ f(84) = f(f(89)) = f^2(89) = f^3(94) = \ldots f^{y}(1004)$.
   $1004 = 84 + 5(y - 1) \Longrightarrow y = 185$. So we now need to reduce
   $f^{185}(1004)$.

   Let’s write out a couple more iterations of this function:
   $\begin{align*}f^{185}(1004)&=f^{184}(1001)=f^{183}(998)=f^{184}(1003)=f^{183}(1000)\\
   &=f^{182}(997)=f^{183}(1002)=f^{182}(999)=f^{183}(1004)\end{align*}$
   So this function reiterates with a period of 2 for $x$. It might be tempting at first
   to assume that $f(1004) = 1001$ is the answer; however, that is not true since the
   solution occurs slightly before that. Start at $f^3(1004)$:
   $f^{3}(1004)=f^{2}(1001)=f(998)=f^{2}(1003)=f(1000)=997$

   Note that we should also be suspicious if our answer is $1001$- it is a $4$-digit
   number, and we were not asked to, say, divide our number by $13$.
*)

Require Import Coq.ZArith.ZArith.

Open Scope Z_scope.

Theorem aime_1984_p7:
  forall (f : Z -> Z),
  (forall n, 1000 <= n -> f n = n - 3) ->
  (forall n, n < 1000 -> f n = f (f (n + 5))) ->
  f 84 = 997.
Proof.
Admitted.