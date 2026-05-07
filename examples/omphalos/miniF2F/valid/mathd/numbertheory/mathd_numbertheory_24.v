(* miniF2F problem: mathd_numbertheory_24
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the tens digit in the sum $11^1 + 11^2 + 11^3 + \ldots + 11^9$? Show that it
   is 5.

   Informal proof:
   First of all, we notice that $11 = 1 + 10,$ and so we write $11^n$ as follows: $$(1 +
   10)^n = \binom{n}{0} \cdot 1^n + \binom{n}{1} \cdot 1^{n-1} \cdot 10^{1} +
   \binom{n}{2} \cdot 1^{n-2} \cdot 10^{2} + \cdots$$ We can see that every term after
   the first two in our expansion has at least two powers of $10,$ therefore they will
   not contribute to the tens digit of anything. Meanwhile, the first term is always
   $1,$ and the second term can be simplified to $10n.$

   Therefore, we have: \begin{align*}
   &11^1 + 11^2 + 11^3 + \cdots + 11^9 \\
   &\qquad\equiv (1 + 10) + (1 + 20) + \cdots + (1 + 90) \pmod{100}. \\
   &\qquad\equiv 459 \equiv 59 \pmod{100}.
   \end{align*} Thus, the tens digit must be $5.$
*)

Require Import List.
Import ListNotations.
Require Import Arith.

Theorem mathd_numbertheory_24 :
  (fold_right plus 0 (map (fun k => 11 ^ k) (seq 1 9))) mod 100 = 59.
Proof.
Admitted.