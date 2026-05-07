(* miniF2F problem: mathd_numbertheory_629
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose $t$ is a positive integer such that $\mathop{\text{lcm}}[12,t]^3=(12t)^2$.
   What is the smallest possible value for $t$? Show that it is 18.

   Informal proof:
   Recall the identity $\mathop{\text{lcm}}[a,b]\cdot \gcd(a,b)=ab$, which holds for all
   positive integers $a$ and $b$. Applying this identity to $12$ and $t$, we obtain
   $$\mathop{\text{lcm}}[12,t]\cdot \gcd(12,t) = 12t,$$and so (cubing both sides)
   $$\mathop{\text{lcm}}[12,t]^3 \cdot \gcd(12,t)^3 = (12t)^3.$$Substituting $(12t)^2$
   for $\mathop{\text{lcm}}[12,t]^3$ and dividing both sides by $(12t)^2$, we have
   $$\gcd(12,t)^3 = 12t,$$so in particular, $12t$ is the cube of an integer. Since
   $12=2^2\cdot 3^1$, the smallest cube of the form $12t$ is $2^3\cdot 3^3$, which is
   obtained when $t=2^1\cdot 3^2 = 18$. This tells us that $t\ge 18$.

   We must check whether $t$ can be $18$. That is, we must check whether
   $\mathop{\text{lcm}}[12,18]^3=(12\cdot 18)^2$. In fact, this equality does hold (both
   sides are equal to $6^6$), so the smallest possible value of $t$ is confirmed to be
   $18$.
*)

Require Import Arith.
Require Import Nat.

Definition Least (P:nat->Prop) n :=
 P n /\ forall m, P m -> n <= m.

Theorem mathd_numbertheory_629:
  Least (fun t => t > 0 /\ (Nat.lcm 12 t)^3 = (12 * t)^2) 18.
Proof.
Admitted.
