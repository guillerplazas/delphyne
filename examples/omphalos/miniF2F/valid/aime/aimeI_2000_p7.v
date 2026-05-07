(* miniF2F problem: aimeI_2000_p7
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $x,$ $y,$ and $z$ are three positive numbers that satisfy the equations
   $xyz = 1,$ $x + \frac {1}{z} = 5,$ and $y + \frac {1}{x} = 29.$ Then $z + \frac
   {1}{y} = \frac {m}{n},$ where $m$ and $n$ are [[relatively prime]] positive integers.
   Find $m + n$.


   note: this is the type of problem that makes you think symmetry, but actually can be
   solved easily with substitution, and other normal technniques Show that it is 005.

   Informal proof:
   We can rewrite $xyz=1$ as $\frac{1}{z}=xy$.

   Substituting into one of the given equations, we have 
   $x+xy=5$
   $x(1+y)=5$
   $\frac{1}{x}=\frac{1+y}{5}.$

   We can substitute back into $y+\frac{1}{x}=29$ to obtain
   $y+\frac{1+y}{5}=29$
   $5y+1+y=145$
   $y=24.$

   We can then substitute once again to get
   $x=\frac15$
   $z=\frac{5}{24}.$
   Thus, $z+\frac1y=\frac{5}{24}+\frac{1}{24}=\frac{1}{4}$, so $m+n=005$.
*)

Require Import Coq.Reals.Reals.
Require Import Coq.QArith.QArith.

Open Scope R_scope.

Theorem aimeI_2000_p7:
  forall (x y z : R) (m : Q),
    (0 < x /\ 0 < y /\ 0 < z) ->
    x * y * z = 1 ->
    x + /z = 5 ->
    y + /x = 29 ->
    z + /y = Q2R m ->
    Qgt m 0 ->
    Qred m = m ->
    (Zpos (Qden m) + Qnum m)%Z = 5%Z.

Proof.
Admitted.
