(* miniF2F problem: aime_1991_p6
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose $r^{}_{}$ is a [[real number]] for which
   <div style=''text-align:center''>$
   \left\lfloor r + \frac{19}{100} \right\rfloor + \left\lfloor r + \frac{20}{100}
   \right\rfloor + \left\lfloor r + \frac{21}{100} \right\rfloor + \cdots + \left\lfloor
   r + \frac{91}{100} \right\rfloor = 546.
   $</div>
   Find $\lfloor 100r \rfloor$. (For real $x^{}_{}$, $\lfloor x \rfloor$ is the [[floor
   function|greatest integer]] less than or equal to $x^{}_{}$.) Show that it is 743.

   Informal proof:
   There are $91 - 19 + 1 = 73$ numbers in the [[sequence]]. Since the terms of the
   sequence can be at most $1$ apart, all of the numbers in the sequence can take one of
   two possible values. Since $\frac{546}{73} = 7 R 35$, the values of each of the terms
   of the sequence must be either $7$ or $8$. As the remainder is $35$, $8$ must take on
   $35$ of the values, with $7$ being the value of the remaining $73 - 35 = 38$ numbers.
   The 39th number is $\lfloor r+\frac{19 + 39 - 1}{100}\rfloor= \lfloor
   r+\frac{57}{100}\rfloor$, which is also the first term of this sequence with a value
   of $8$, so $8 \le r + \frac{57}{100} < 8.01$. Solving shows that $\frac{743}{100} \le
   r < \frac{744}{100}$, so $743\le 100r < 744$, and $\lfloor 100r \rfloor = 743$.
*)

Require Import Reals.
Require Import ZArith.
Require Import List.
Require Import Lia.

Open Scope R_scope.

Definition range_sum (r : R) := 
  fold_left Z.add
    (map (fun k => Int_part (r + IZR (Z.of_nat k) / 100))
         (seq 19 73))
    0%Z.

Theorem aime_1991_p6 :
  forall r : R,
  range_sum r = 546%Z ->
  Int_part (100 * r) = 743%Z.

Proof.
Admitted.
