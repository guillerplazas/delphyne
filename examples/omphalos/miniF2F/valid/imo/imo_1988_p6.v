(* miniF2F problem: imo_1988_p6
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $a$ and $b$ be positive integers such that $ab + 1$ divides $a^{2} + b^{2}$. Show
   that
   $
   \frac {a^{2} + b^{2}}{ab + 1}
   $
   is the square of an integer.

   Informal proof:
   Choose integers $a,b,k$ such that $a^2+b^2=k(ab+1)$
   Now, for fixed $k$, out of all pairs $(a,b)$ choose the one with the lowest value of
   $\min(a,b)$. Label $b'=\min(a,b), a'=\max(a,b)$. Thus, $a'^2-kb'a'+b'^2-k=0$ is a
   quadratic in $a'$. Should there be another root, $c'$, the root would satisfy:
   $b'c'\leq a'c'=b'^2-k<b'^2\implies c'<b'$
   Thus, $c'$ isn't a positive integer (if it were, it would contradict the minimality
   condition). But $c'=kb'-a'$, so $c'$ is an integer; hence, $c'\leq 0$. In addition,
   $(a'+1)(c'+1)=a'c'+a'+c'+1=b'^2-k+b'k+1=b'^2+(b'-1)k+1\geq 1$ so that $c'>-1$. We
   conclude that $c'=0$ so that $b'^2=k$.

   This construction works whenever there exists a solution $(a,b)$ for a fixed $k$,
   hence $k$ is always a perfect square.
*)

Require Import Reals.
Require Import Nat.
Require Import ZArith.

Theorem imo_1988_p6 :
  forall (a b : nat),
  0 < a -> 0 < b ->
  (Nat.divide (a * b + 1) (a * a + b * b)) ->
  exists x : nat, 
    (INR x * INR x)%R = (INR (a * a + b * b) / INR (a * b + 1))%R.

Proof.
Admitted.
