(* miniF2F problem: amc12b_2002_p3
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   For how many positive integers $n$ is $n^2 - 3n + 2$ a [[prime]] number?

   $\mathrm{(A)}\ \text{none}
   \qquad\mathrm{(B)}\ \text{one}
   \qquad\mathrm{(C)}\ \text{two}
   \qquad\mathrm{(D)}\ \text{more\ than\ two,\ but\ finitely\ many}
   \qquad\mathrm{(E)}\ \text{infinitely\ many}$ Show that it is \mathrm{(B)}\
   \text{one}.

   Informal proof:
   Factoring, we get $n^2 - 3n + 2 = (n-2)(n-1)$. Either $n-1$ or $n-2$ is odd, and the
   other is even.  Their product must yield an even number.  The only prime that is even
   is $2$, which is when $n$ is $3$ or $0$. Since $0$ is not a positive number, the
   answer is $\mathrm{(B)}\ \text{one}$.
*)

Require Import Nat.
Require Import ZArith.
Require Import Znumtheory.

Theorem amc12b_2002_p3 :
  forall (n : Z),
  (n > 0)%Z -> 
  prime (n * n - 3 * n + 2)%Z ->
  n = 3%Z.

Proof.
Admitted.
