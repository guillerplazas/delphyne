(* miniF2F problem: mathd_numbertheory_412
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $x \equiv 4 \pmod{19}$ and $y \equiv 7 \pmod{19}$, then find the remainder when
   $(x + 1)^2 (y + 5)^3$ is divided by 19. Show that it is 13.

   Informal proof:
   If $x \equiv 4 \pmod{19}$ and $y \equiv 7 \pmod{19}$, then \begin{align*}
   (x + 1)^2 (y + 5)^3 &\equiv 5^2 \cdot 12^3 \\
   &\equiv 25 \cdot 1728 \\
   &\equiv 6 \cdot 18 \\
   &\equiv 108 \\
   &\equiv 13 \pmod{19}.
   \end{align*}
*)

Require Import Nat.
Require Import ZArith.
Open Scope nat_scope.

Theorem mathd_numbertheory_412 :
  forall (x y : nat),
  (x mod 19 = 4) ->
  (y mod 19 = 7) ->
  ((x + 1)^2 * (y + 5)^3) mod 19 = 13.
Proof.
Admitted.