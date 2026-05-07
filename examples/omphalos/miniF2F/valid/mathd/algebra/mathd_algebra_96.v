(* miniF2F problem: mathd_algebra_96
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $x$, $y$, and $z$ are positive real numbers satisfying: \begin{align*}
   \log x - \log y &= a, \\
   \log y - \log z &= 15, \text{ and} \\
   \log z - \log x &= -7, \\
   \end{align*}where $a$ is a real number, what is $a$? Show that it is -8.

   Informal proof:
   Notice that by the logarithmic identity $\log(x) - \log(y) = \log\frac{x}{y}$, the
   equations are equivalent to $\log\frac{x}{y}=a$, $\log\frac{y}{z}=15$, and
   $\log\frac{z}{x}=-7$ respectively. Adding all three equations together yields
   $\log\frac{x}{y} + \log\frac{y}{z} + \log\frac{z}{x} = a + 15 - 7$. From the identity
   $\log (x) + \log (y) = \log (xy)$, we obtain
   $\log\left(\frac{x}{y}\cdot\frac{y}{z}\cdot\frac{z}{x}\right) = a + 8$. Cancelations
   result in $\log(1) = a + 8$. Since $\log(1) = 0$, we find $a = -8$.
*)

Require Import Reals.
Require Import Lra.
Open Scope R_scope.

Theorem mathd_algebra_96:
  forall (x y z a : R),
  (0 < x) -> (0 < y) -> (0 < z) ->
  (ln x - ln y = a) ->
  (ln y - ln z = 15) ->
  (ln z - ln x = -7) ->
  a = -8.
Proof.
Admitted.
