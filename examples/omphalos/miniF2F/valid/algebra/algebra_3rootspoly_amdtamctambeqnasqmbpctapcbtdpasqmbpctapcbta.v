(* miniF2F problem: algebra_3rootspoly_amdtamctambeqnasqmbpctapcbtdpasqmbpctapcbta
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any complex numbers $a$, $b$, $c$, $d$, $(a-d)(a-c)(a-b) = -(((a^2 -
   (b+c)a) + cb)d) + (a^2 - (b+c)a + cb)a$.

   Informal proof:
   By expansion, we have that $(a-d)(a-c) = a^2-ad-ac+cd$, so $(a-d)(a-c)(a-b) =
   (a^2-ad-ac+cd)(a-b) = a^3-da^2-ca^2+acd-ba^2+abd+abc-bcd$
   As a result, $-(((a^2 - (b+c)a) + cb)d) + (a^2 - (b+c)a + cb)a =
   -d(a^2-ab-ac+bc)+a^3-ba^2-ca^2+abc = a^3-da^2-ca^2+acd-ba^2+abd+abc-bcd =
   (a-d)(a-c)(a-b)$.
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem algebra_3rootspoly_amdtamctambeqnasqmbpctapcbtdpasqmbpctapcbta
  (a b c d : C) :
  (a - d) * (a - c) * (a - b) = -(((a ^ 2 - (b + c) * a) + c * b) * d) + (a ^ 2 - (b + c) * a + c * b) * a.

Proof.
Admitted.
