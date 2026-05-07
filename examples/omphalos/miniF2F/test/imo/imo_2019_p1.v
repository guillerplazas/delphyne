(* miniF2F problem: imo_2019_p1
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   'Let $\mathbb{Z}$ be the set of integers. Determine all functions $f : \mathbb{Z} \to
   \mathbb{Z}$ such that, for all
   ''integers $a$ and $b$, $f(2a) + 2f(b) = f(f(a + b)).$''

   Informal proof:
   Let us substitute $0$ in for $a$ to get
   $f(0) + 2f(b) = f(f(b)).$

   Now, since the domain and range of $f$ are the same, we can let $x = f(b)$ and $f(0)$
   equal some constant $c$ to get
   $c + 2x = f(x).$
   Therefore, we have found that '''all''' solutions must be of the form $f(x) = 2x +
   c.$

   Plugging back into the original equation, we have: $4a + c + 4b + 2c = 4a + 4b + 2c +
   c$ which is true. Therefore, we know that $f(x) = 2x + c$ satisfies the above for any
   '''integral''' constant c, and that this family of equations is unique.
*)

Require Import ZArith.
Open Scope Z_scope.

Theorem imo_2019_p1 (f : Z -> Z) :
  (forall a b, f (2 * a) + (2 * f b) = f (f (a + b))) <->
  ((forall z, f z = 0) \/ exists c, forall z, f z = 2 * z + c).
Proof.
Admitted.
