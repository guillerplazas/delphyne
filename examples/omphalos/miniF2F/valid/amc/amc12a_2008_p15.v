(* miniF2F problem: amc12a_2008_p15
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $k={2008}^{2}+{2}^{2008}$. What is the units digit of $k^2+2^k$?

   $\mathrm{(A)}\ 0\qquad\mathrm{(B)}\ 2\qquad\mathrm{(C)}\ 4\qquad\mathrm{(D)}\
   6\qquad\mathrm{(E)}\ 8$ Show that it is D.

   Informal proof:
   $k \equiv 2008^2 + 2^{2008} \equiv 8^2 + 2^4 \equiv 4+6 \equiv 0 \pmod{10}$. 

   So, $k^2 \equiv 0 \pmod{10}$. Since $k = 2008^2+2^{2008}$   is a multiple of four and
   the units digit of powers of two repeat in cycles of four, $2^k \equiv 2^4 \equiv 6
   \pmod{10}$. 

   Therefore, $k^2+2^k \equiv 0+6 \equiv 6 \pmod{10}$. So the units digit is $6
   \Rightarrow D$.
*)

Require Import Coq.Arith.Arith.
Require Import Coq.ZArith.ZArith.

Theorem amc12a_2008_p15 :
  forall k : nat,
  k = 2008^2 + 2^2008 ->
  (k^2 + 2^k) mod 10 = 6.
Proof.
Admitted.