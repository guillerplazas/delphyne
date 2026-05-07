(* miniF2F problem: mathd_numbertheory_430
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   If $A$, $B$, and $C$ represent three distinct digits from 1 to 9 and they satisfy the
   following equations, what is the value of the sum $A+B+C$? (In the equation below,
   $AA$ represents a two-digit number both of whose digits are $A$.)
   $$A+B=C$$$$AA-B=2\times C$$$$C\times B=AA+A$$ Show that it is 8.

   Informal proof:
   We start off by replacing $C$ with $A+B$ and changing the form of the two-digit
   integer in the second equation. \begin{align*}
   10A+A-B&=2\times(A+B)\quad\Rightarrow\\
   11A-B&=2A+2B\quad\Rightarrow\\
   9A&=3B\quad\Rightarrow\\
   3A&=B
   \end{align*}Now we replace $C$, change the two-digit integer, and then substitute $B$
   with $3A$ in the third equation. \begin{align*}
   (A+B)\times B&=10A+A+A\quad\Rightarrow\\
   &=12A\quad\Rightarrow\\
   (A+3A)\times3A&=12A\quad\Rightarrow\\
   (4A)\times3A&=12A\quad\Rightarrow\\
   12(A)^2&=12A
   \end{align*}For $(A)^2$ to equal $A$, $A$ must equal 1. Since $3A=B$, $B=3$. That
   means $A+B=C=4$. So the sum of the three digits is $1+3+4=8$.
*)

Require Import Arith.
Require Import Nat.

Theorem mathd_numbertheory_430 :
  forall (A B C : nat),
  (1 <= A <= 9) ->
  (1 <= B <= 9) ->
  (1 <= C <= 9) ->
  A <> B ->
  A <> C ->
  B <> C ->
  A + B = C ->
  (10 * A + A - B = 2 * C) ->
  (C * B = 10 * A + A + A) ->
  A + B + C = 8.
Proof.
Admitted.