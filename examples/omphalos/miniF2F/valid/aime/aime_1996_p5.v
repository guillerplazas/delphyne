(* miniF2F problem: aime_1996_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that the [[root]]s of $x^3+3x^2+4x-11=0$ are $a$, $b$, and $c$, and that the
   roots of $x^3+rx^2+sx+t=0$ are $a+b$, $b+c$, and $c+a$. Find $t$. Show that it is 23.

   Informal proof:
   By [[Vieta's formulas]] on the polynomial $P(x) = x^3+3x^2+4x-11 = (x-a)(x-b)(x-c) =
   0$, we have $a + b + c = s = -3$, $ab + bc + ca = 4$, and $abc = 11$. Then
   <center>$t = -(a+b)(b+c)(c+a) = -(s-a)(s-b)(s-c) = -(-3-a)(-3-b)(-3-c)$</center>
   This is just the definition for $-P(-3) = 023$.
*)

Require Import Reals.
Require Import Coq.Reals.Reals.

Open Scope R_scope.

Theorem aime_1996_p5 :
  forall (a b c r s t : R) (f g : R -> R),
  (forall x, f x = x^3 + 3*x^2 + 4*x - 11) ->
  (forall x, g x = x^3 + r*x^2 + s*x + t) ->
  f a = 0 ->
  f b = 0 ->
  f c = 0 ->
  g (a + b) = 0 ->
  g (b + c) = 0 ->
  g (c + a) = 0 ->
  a <> b ->
  b <> c ->
  c <> a ->
  t = 23.
Proof.
Admitted.