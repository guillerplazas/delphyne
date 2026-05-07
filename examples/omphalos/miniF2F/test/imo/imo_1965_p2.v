(* miniF2F problem: imo_1965_p2
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Consider the system of equations
   $a_{11}x_1 + a_{12}x_2 + a_{13}x_3 = 0$
   $a_{21}x_1 + a_{22}x_2 + a_{23}x_3 = 0$
   $a_{31}x_1 + a_{32}x_2 + a_{33}x_3 = 0$
   with unknowns $x_1$, $x_2$, $x_3$. The coefficients satisfy the conditions:

   (a) $a_{11}$, $a_{22}$, $a_{33}$ are positive numbers;

   (b) the remaining coefficients are negative numbers;

   (c) in each equation, the sum of the coefficients is positive.

   Prove that the given system has only the solution $x_1 = x_2 = x_3 = 0$.

   Informal proof:
   Clearly if the $x_i$ are all equal, then they are equal to 0. Now let's assume WLOG
   that $x_1=0$. If $x_2$ or $x_3$ is 0, then the other is clearly zero, so let's
   consider the case where neither are 0. $a_{12}$ and $a_{21}$ are negative, so exactly
   one of $x_2$ or $x_3$ is positive. Unfortunately this means that one of $a_{22}x_2 +
   a_{23}x_3$ or $a_{32}x_2 + a_{33}x_3 = 0$ is positive and the other is negative, so
   the equation couldn't possibly be satisfied if $x_2$ or $x_3$ isn't 0. We have
   covered the case where one of the $x_i$ is 0, now let's assume that none of them are
   0.

   If two are positive and one is negative, then when the negative $x_i$ is paired with
   one of the positive $a_i$, the corresponding equation is negative. This is bad. If
   two are negative and one is positive, then when the positive $x_i$ is paired with one
   of the positive $a_i$, the corresponding equation is positive. This is also bad.
   Therefore the $x_i$ all have the same sign.

   Case 1: The $x_i$ are all positive. WLOG $x_1\leq x_2\leq x_3$. Now consider the
   third equation, $a_{31}x_1 + a_{32}x_2 + a_{33}x_3 = 0$. Therefore $x_2(a_{31}
   +a_{32}+a_{33})+ a_{31}(x_1-x_2)+a_{33}(x_3-x_2)= 0$, but all of the terms on the LHS
   are non-negative and the first one is positive, so this is impossible.

   Case 2: The $x_i$ are all negative. WLOG $x_1\geq x_2\geq x_3$. Consider the third
   equation, $a_{31}x_1 + a_{32}x_2 + a_{33}x_3 = 0$. Therefore
   $x_3(a_{31}+a_{32}+a_{33})+a_{31}(x_1-x_3)+a_{32}(x_2-x_3)=0$, but all of the terms
   on the LHS are non-positive and the first one is negative, so this is impossible.

   Therefore at least one of the $x_i$ is 0, which implies all of them are 0.
*)

Require Import Reals.
Open Scope R_scope.

Theorem imo_1965_p2
  (x y z : R)
  (a : nat -> R)
  (H0 : (0 < a O)%R /\ (0 < a 4%nat)%R /\ (0 < a 8%nat)%R)
  (H1 : (a 1%nat < 0)%R /\ (a 2%nat < 0)%R)
  (H2 : (a 3%nat < 0)%R /\ (a 5%nat < 0)%R)
  (H3 : (a 6%nat < 0)%R /\ (a 7%nat < 0)%R)
  (H4 : (0 < a O + a 1%nat + a 2%nat)%R)
  (H5 : (0 < a 3%nat + a 4%nat + a 5%nat)%R)
  (H6 : (0 < a 6%nat + a 7%nat + a 8%nat)%R)
  (H7 : (a O * x + a 1%nat * y + a 2%nat * z = 0)%R)
  (H8 : (a 3%nat * x + a 4%nat * y + a 5%nat * z = 0)%R)
  (H9 : (a 6%nat * x + a 7%nat * y + a 8%nat * z = 0)%R) :
  (x = 0 /\ y = 0 /\ z = 0)%R.

Proof.
Admitted.
