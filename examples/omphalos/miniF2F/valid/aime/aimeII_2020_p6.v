(* miniF2F problem: aimeII_2020_p6
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Define a sequence recursively by $t_1 = 20$, $t_2 = 21$, and$t_n =
   \frac{5t_{n-1}+1}{25t_{n-2}}$for all $n \ge 3$. Then $t_{2020}$ can be expressed as
   $\frac{p}{q}$, where $p$ and $q$ are relatively prime positive integers. Find $p+q$.
   Show that it is 626.

   Informal proof:
   Let $t_n=\frac{s_n}{5}$. Then, we have $s_n=\frac{s_{n-1}+1}{s_{n-2}}$ where $s_1 =
   100$ and $s_2 = 105$. By substitution, we find $s_3 = \frac{53}{50}$,
   $s_4=\frac{103}{105\cdot50}$, $s_5=\frac{101}{105}$, $s_6=100$, and $s_7=105$. So
   $s_n$ has a period of $5$. Thus $s_{2020}=s_5=\frac{101}{105}$. So,
   $\frac{101}{105\cdot 5}\implies 101+525=626$.
*)

Require Import Reals.
Require Import QArith.QArith.
Require Import Lia.
Require Import ZArith.

Theorem aimeII_2020_p6 :
  forall t : nat -> Q,
  t 1%nat = 20#1 ->
  t 2%nat = 21#1 ->
  (forall n : nat, (n >= 3)%nat ->
    t n = Qdiv (Qplus (Qmult (inject_Z 5) (t (n-1)%nat)) (inject_Z 1))
              (Qmult (inject_Z 25) (t (n-2)%nat))) ->
  exists p : Z, exists q : positive,
    Z.gcd p (Z.pos q) = 1%Z /\ p#q == t 2020%nat /\
    Z.add p (Z.pos q) = Z.of_nat 626.
Proof.
Admitted.
