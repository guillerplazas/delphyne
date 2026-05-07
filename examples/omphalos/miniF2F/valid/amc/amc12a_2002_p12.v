(* miniF2F problem: amc12a_2002_p12
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Both roots of the quadratic equation $x^2 - 63x + k = 0$ are prime numbers. The
   number of possible values of $k$ is 

   $\text{(A)}\ 0 \qquad \text{(B)}\ 1 \qquad \text{(C)}\ 2 \qquad \text{(D)}\ 4 \qquad
   \text{(E) more than 4}$ Show that it is \text{(B)}\ 1.

   Informal proof:
   Consider a general quadratic with the coefficient of $x^2$ being $1$ and the roots
   being $r$ and $s$. It can be factored as $(x-r)(x-s)$ which is just $x^2-(r+s)x+rs$.
   Thus, the sum of the roots is the negative of the coefficient of $x$ and the product
   is the constant term. (In general, this leads to [[Vieta's Formulas]]).

   We now have that the sum of the two roots is $63$ while the product is $k$. Since
   both roots are primes, one must be $2$, otherwise the sum would be even. That means
   the other root is $61$ and the product must be $122$. Hence, our answer is
   $\text{(B)}\ 1$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
From Coq Require Import ZArith.
From Coq Require Import Lia.
From Coq Require Import Znumtheory.  

Open Scope R_scope.

Theorem amc12a_2002_p12 :
  forall (f : R -> R) (k : R) (a b : Z),
    (forall x : R, f x = x ^ 2 - 63 * x + k) ->
    f (IZR a) = 0 ->
    f (IZR b) = 0 ->
    a <> b ->
    prime a /\ prime b ->
    k = 122.


Proof.
Admitted.
