(* miniF2F problem: mathd_numbertheory_769
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the remainder when $129^{34}+96^{38}$ is divided by $11$? Show that it is 9.

   Informal proof:
   We use the property that $a \equiv b \pmod{m}$ implies $a^c \equiv b^c \pmod{m}$.

   Since $129 \equiv -3 \pmod{11}$ and $96 \equiv -3 \pmod{11}$, we have 
   $$129^{34}+96^{38} \equiv (-3)^{34}+(-3)^{38} \equiv 3^{34}+3^{38} \pmod{11}.$$Since
   $3^5 \equiv 1 \pmod{11},$ we can see that $3^{34} = (3^5)^{6} \cdot 3^4$ and $3^{38}
   = (3^5)^{7} \cdot 3^3.$

   Then,  \begin{align*}
   129^{34}+96^{38}&\equiv (3^5)^{6} \cdot 3^4 + (3^5)^{7} \cdot 3^3\\
   & \equiv 3^4 + 3^3\\
   & \equiv 81 + 27\\
   & \equiv 108 \\
   &\equiv 9 \pmod{11}.
   \end{align*}
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem mathd_numbertheory_769 :
  (129^34 + 96^38) mod 11 = 9.
Proof.
Admitted.