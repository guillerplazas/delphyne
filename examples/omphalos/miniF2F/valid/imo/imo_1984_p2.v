(* miniF2F problem: imo_1984_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Find one pair of positive integers $a,b$ such that $ab(a+b)$ is not divisible by $7$,
   but $(a+b)^7-a^7-b^7$ is divisible by $7^7$.

   Informal proof:
   So we want $7 \nmid ab(a+b)$ and $7^7 | (a+b)^7-a^7-b^7 = 7ab(a+b)(a^2+ab+b^2)^2$, so
   we want $7^3 | a^2+ab+b^2$.
   Now take e.g. $a=2,b=1$ and get $7|a^2+ab+b^2$. Now by some standard methods like
   Hensels Lemma (used to the polynomial $x^2+x+1$, so $b$ seen as constant from now) we
   get also some $\overline{a}$ with $7^3 | \overline{a}^2+\overline{a}b+b^2$ and
   $\overline{a} \equiv a \equiv 2 \mod 7$, so $7\nmid \overline{a}b(\overline{a}+b)$
   and we are done. (in this case it gives $\overline{a}=325$)
*)

Require Import Nat.
Require Import Arith.

Theorem imo_1984_p2 :
  forall (a b : nat),
    0 < a -> 0 < b ->
    ~ (Nat.divide 7 a) ->
    ~ (Nat.divide 7 b) ->
    ~ (Nat.divide 7 (a + b)) ->
    (Nat.divide (7^7) ((a + b)^7 - a^7 - b^7)) ->
    19 <= a + b.

Proof.
Admitted.
