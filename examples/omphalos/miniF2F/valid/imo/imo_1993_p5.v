(* miniF2F problem: imo_1993_p5
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $\mathbb{N} = \{1,2,3, \ldots\}$. Determine if there exists a strictly increasing
   function $f: \mathbb{N} \mapsto \mathbb{N}$ with the following properties:

   (i) $f(1) = 2$;

   (ii) $f(f(n)) = f(n) + n, (n \in \mathbb{N})$.

   Informal proof:
   Here is my Solution https://artofproblemsolving.com/community/q2h62193p16226748

   Find as ≈ Ftheftics
*)

Require Import Coq.Numbers.Natural.Abstract.NBase.
Require Import Coq.Arith.Arith.

Theorem imo_1993_p5 :
  exists f : nat -> nat,
    f 1 = 2 /\
    (forall n, f (f n) = f n + n) /\
    (forall n m, n < m -> f n < f m).
Proof.
Admitted.