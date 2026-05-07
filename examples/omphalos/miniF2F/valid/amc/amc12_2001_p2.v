(* miniF2F problem: amc12_2001_p2
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $P(n)$ and $S(n)$ denote the product and the sum, respectively, of the digits
   of the integer $n$. For example, $P(23) = 6$ and $S(23) = 5$. Suppose $N$ is a
   two-digit number such that $N = P(N)+S(N)$. What is the units digit of $N$?

   $\text{(A)}\ 2\qquad \text{(B)}\ 3\qquad \text{(C)}\ 6\qquad \text{(D)}\ 8\qquad
   \text{(E)}\ 9$ Show that it is (\text{E})9.

   Informal proof:
   Denote $a$ and $b$ as the tens and units digit of $N$, respectively. Then $N =
   10a+b$. It follows that $10a+b=ab+a+b$, which implies that $9a=ab$. Since $a\neq0$,
   $b=9$. So the units digit of $N$ is $(\text{E})9$.
*)

Require Import Coq.Arith.Arith.

Theorem amc12_2001_p2 (a b n : nat) :
  (1 <= a <= 9) -> (0 <= b <= 9) -> (n = 10 * a + b) -> (n = a * b + a + b) -> 
  (b = 9).
Proof.
Admitted.