(* miniF2F problem: mathd_numbertheory_668
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Given $m\geq 2$, denote by $b^{-1}$ the inverse of $b\pmod{m}$. That is, $b^{-1}$ is
   the residue for which $bb^{-1}\equiv 1\pmod{m}$. Sadie wonders if $(a+b)^{-1}$ is
   always congruent to $a^{-1}+b^{-1}$ (modulo $m$). She tries the example $a=2$, $b=3$,
   and $m=7$. Let $L$ be the residue of $(2+3)^{-1}\pmod{7}$, and let $R$ be the residue
   of $2^{-1}+3^{-1}\pmod{7}$, where $L$ and $R$ are integers from $0$ to $6$
   (inclusive). Find $L-R$. Show that it is 1.

   Informal proof:
   The inverse of $5\pmod{7}$ is 3, since $5\cdot3 \equiv 1\pmod{7}$. Also, inverse of
   $2\pmod{7}$ is 4, since $2\cdot 4\equiv 1\pmod{7}$. Finally, the inverse of
   $3\pmod{7}$ is 5 (again because $5\cdot3 \equiv 1\pmod{7}$). So the residue of
   $2^{-1}+3^{-1}$ is the residue of $4+5\pmod{7}$, which is $2$. Thus $L-R=3-2=1$.
   Since the left-hand side $L$ and the right-hand side $R$ of the equation $$
   (a+b)^{-1} \stackrel{?}{=} a^{-1} + b^{-1} \pmod{m}
   $$are not equal, we may conclude that the equation is not true in general.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_668 (l r : Z) : 
  (0 <= l < 7)%Z -> (0 <= r < 7)%Z ->
  (l * (2 + 3) mod 7 = 1)%Z ->
  (exists a b, (0 <= a < 7)%Z /\ (0 <= b < 7)%Z /\
            (a * 2 mod 7 = 1)%Z /\ (b * 3 mod 7 = 1)%Z /\
            (r = (a + b) mod 7)%Z) ->
  l - r = 1.
Proof.
Admitted.