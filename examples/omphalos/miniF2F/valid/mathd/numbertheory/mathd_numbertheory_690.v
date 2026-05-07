(* miniF2F problem: mathd_numbertheory_690
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Determine the smallest non-negative integer $a$ that satisfies the congruences:
   \begin{align*}
   &a\equiv 2\pmod 3,\\
   &a\equiv 4\pmod 5,\\
   &a\equiv 6\pmod 7,\\
   &a\equiv 8\pmod 9.
   \end{align*} Show that it is 314.

   Informal proof:
   First notice that $a\equiv 8\pmod 9$ tells us that $a\equiv 2\pmod 3$, so once we
   satisfy the former, we have the latter.    So, we focus on the final three
   congruences.  We do so by rewriting them as \begin{align*}
   a&\equiv -1\pmod 5,\\
   a&\equiv -1\pmod 7,\\
   a&\equiv -1\pmod 9.
   \end{align*} Since $\gcd(5,7)=\gcd(7,9)=\gcd(9,5)=1$, the above congruences apply
   that $a\equiv -1\pmod{5\cdot 7\cdot 9}$, or $a\equiv 314\pmod{315}$. So $a$ is of the
   form $314+315n$ for an integer $n$. The smallest non-negative number of this form is
   $314$, which satisfies the original congruences.
*)

Require Import Coq.Arith.Arith.

Theorem mathd_numbertheory_690 :
  314 mod 3 = 2 /\
  314 mod 5 = 4 /\
  314 mod 7 = 6 /\
  314 mod 9 = 8 /\
  (forall n : nat,
    n mod 3 = 2 /\
    n mod 5 = 4 /\
    n mod 7 = 6 /\
    n mod 9 = 8 ->
    314 <= n).

Proof.
Admitted.
