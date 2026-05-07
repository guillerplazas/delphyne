(* miniF2F problem: amc12a_2003_p25
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f(x)= \sqrt{ax^2+bx} $.  For how many [[real number | real]] values of $a$ is
   there at least one [[positive number | positive]] value of $ b $ for which the
   [[domain]] of $f $ and the [[range]] of $ f $ are the same [[set]]?

   $ \mathrm{(A) \ 0 } \qquad \mathrm{(B) \ 1 } \qquad \mathrm{(C) \ 2 } \qquad
   \mathrm{(D) \ 3 } \qquad \mathrm{(E) \ \mathrm{infinitely \ many} }  $ Show that it
   is \mathrm{(B) \ 2 }.

   Informal proof:
   The function $f(x) = \sqrt{x(ax+b)}$ has a [[codomain]] of all non-negative numbers,
   or $0 \le f(x)$. Since the domain and the range of $f$ are the same, it follows that
   the domain of $f$ also satisfies $0 \le x$.

   The function has two zeroes at $x = 0, \frac{-b}{a}$, which must be part of the
   domain. Since the domain and the range are the same set, it follows that
   $\frac{-b}{a}$ is in the codomain of $f$, or $0 \le \frac{-b}{a}$. This implies that
   one (but not both) of $a,b$ is non-positive. The problem states that there is at
   least one positive value of b that works, thus $a$ must be non-positive, $b$ is
   non-negative, and the domain of the function occurs when $x(ax+b) > 0$, or 

   <center>$0 \le x \le \frac{-b}{a}.$</center>

   [[Completing the square]], $f(x) = \sqrt{a\left(x + \frac{b}{2a}\right)^2 -
   \frac{b^2}{4a}} \le \sqrt{\frac{-b^2}{4a}}$ by the [[Trivial Inequality]] (remember
   that $a \le 0$). Since $f$ is continuous and assumes this maximal value at $x =
   \frac{-b}{2a}$, it follows that the range of $f$ is 

   <center>$0 \le f(x) \le \sqrt{\frac{-b^2}{4a}}.$</center>

   As the domain and the range are the same, we have that $\frac{-b}{a} =
   \sqrt{\frac{-b^2}{4a}} = \frac{b}{2\sqrt{-a}} \Longrightarrow a(a+4) = 0$ (we can
   divide through by $b$ since it is given that $b$ is positive). Hence $a = 0, -4$,
   which both we can verify work, and the answer is $\mathbf{(C)}$.
*)

Require Import Reals.
Require Import Sets.Ensembles.
Require Import Sets.Image.

Open Scope R_scope.

Theorem amc12a_2003_p25 :
  forall (a b : R) (f : R -> R),
    b > 0 ->
    (forall x : R, f x = sqrt (a * x^2 + b * x)) ->
    (forall x : R, In R (fun y => 0 <= f y) x <-> 
      exists z : R, In R (fun y => 0 <= f y) z /\ f z = x) ->
    a = 0 \/ a = -4.

Proof.
Admitted.
