(* miniF2F problem: imo_2001_p6
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   $K > L > M > N$ are positive integers such that $KM + LN = (K + L - M + N)(-K + L + M
   + N)$. Prove that $KL + MN$ is not prime.

   Informal proof:
   First, $(KL+MN)-(KM+LN)=(K-N)(L-M)>0$ as $K>N$ and $L>M$.  Thus, $KL+MN>KM+LN$.  

   Similarly, $(KM+LN)-(KN+LM)=(K-L)(M-N)>0$ since $K>L$ and $M>N$.  Thus,
   $KM+LN>KN+LM$.  

   Putting the two together, we have
   $KL+MN>KM+LN>KN+LM$

   Now, we have:
   $(K+L-M+N)(-K+L+M+N)=KM+LN$
   $-K^2+KM+L^2+LN+KM-M^2+LN+N^2=KM+LN$
   $L^2+LN+N^2=K^2-KM+M^2$
   So, we have:
   $(KM+LN)(L^2+LN+N^2)=KM(L^2+LN+N^2)+LN(L^2+LN+N^2)$
   $=KM(L^2+LN+N^2)+LN(K^2-KM+M^2)$
   $=KML^2+KMN^2+K^2LN+LM^2N$
   $=(KL+MN)(KN+LM)$
   Thus, it follows that $(KM+LN) \mid (KL+MN)(KN+LM).$  
   Now, since $KL+MN>KM+LN$ if $KL+MN$ is prime, then there are no common factors
   between the two.  So, in order to have $(KM+LN)\mid (KL+MN)(KN+LM),$ we would have to
   have $(KM+LN) \mid (KN+LM).$ This is impossible as $KM+LN>KN+LM$.  Thus, $KL+MN$ must
   be composite.
*)

Require Import Nat.
Require Import Arith.
Require Import Znumtheory.
Require Import ZArith.

Theorem imo_2001_p6 :
  forall (a b c d : nat),
    (0 < a)%nat /\ (0 < b)%nat /\ (0 < c)%nat /\ (0 < d)%nat ->
    (d < c)%nat ->
    (c < b)%nat ->
    (b < a)%nat ->
    (a * c + b * d = (b + d + a - c) * (b + d + c - a))%nat ->
    ~ prime (Z.of_nat (a * b + c * d)).

Proof.
Admitted.
