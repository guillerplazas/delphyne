(* miniF2F problem: amc12a_2021_p12
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   All the roots of the polynomial $z^6-10z^5+Az^4+Bz^3+Cz^2+Dz+16$ are positive
   integers, possibly repeated. What is the value of $B$?

   $\textbf{(A) }{-}88 \qquad \textbf{(B) }{-}80 \qquad \textbf{(C) }{-}64 \qquad
   \textbf{(D) }{-}41\qquad \textbf{(E) }{-}40$ Show that it is \textbf{(A) }{-}88.

   Informal proof:
   By Vieta's formulas, the sum of the six roots is $10$ and the product of the six
   roots is $16$. By inspection, we see the roots are $1, 1, 2, 2, 2,$ and $2$, so the
   function is $(z-1)^2(z-2)^4=(z^2-2z+1)(z^4-8z^3+24z^2-32z+16)$. Therefore,
   calculating just the $z^3$ terms, we get $B = -32 - 48 - 8 = \textbf{(A) }{-}88$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope R_scope.
Open Scope C_scope.

Theorem amc12a_2021_p12 
  (a b c d : R)
  (f : C -> C)
  (h0 : forall z, f z = z^6 - 10 * z^5 + a * z^4 + b * z^3 + c * z^2 + d * z + 16)
  (h1 : forall z, f z = 0 -> 
        Im z = 0 /\ (0 < Re z)%R /\ IZR (floor (Re z)) = Re z) :
  b = -88.

Proof.
Admitted.
