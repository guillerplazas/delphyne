(* miniF2F problem: mathd_numbertheory_326
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   The product of three consecutive integers is 720. What is the largest of these
   integers? Show that it is 10.

   Informal proof:
   Let the integers be $n-1$, $n$, and $n+1$.  Their product is $n^3-n$.  Thus
   $n^3=720+n$.  The smallest perfect cube greater than $720$ is $729=9^3$, and indeed
   $729=720+9$.  So $n=9$ and the largest of the integers is $n+1=10$.
*)

(* 
Step 1: Define the theorem with parameter n : nat.

Step 2: Assume that (n - 1) * n * (n + 1) = 720.

Step 3: Show that n + 1 = 10.
*)

Theorem mathd_numbertheory_326 :
  forall n : nat,
    (n - 1) * n * (n + 1) = 720 ->
    n + 1 = 10.
Proof.
Admitted.