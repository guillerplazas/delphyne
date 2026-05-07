(* miniF2F problem: mathd_algebra_313
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Complex numbers are often used when dealing with alternating current (AC) circuits.
   In the equation $V = IZ$, $V$ is voltage, $I$ is current, and $Z$ is a value known as
   impedance. If $V = 1+i$ and $Z=2-i$, find $I$. Show that it is \frac{1}{5} +
   \frac{3}{5}i.

   Informal proof:
   We have $$
   I = \frac{V}{Z} = \frac{1+i}{2-i}.
   $$ Multiplying the numerator and denominator by the conjugate of the denominator, we
   get $$
   I = \frac{1+i}{2-i} \cdot \frac{2+i}{2+i} = \frac{1(2) + 1(i) + i(2) + i(i)}{2(2) +
   2(i) - i(2) - i(i)} = \frac{1+3i}{5} = \frac{1}{5} + \frac{3}{5}i.
   $$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem mathd_algebra_313
  (v i z : C)
  (h0 : v = i * z)
  (h1 : v = 1 + Ci)
  (h2 : z = 2 - Ci) :
  i = 1/5 + 3/5 * Ci.

Proof.
Admitted.
