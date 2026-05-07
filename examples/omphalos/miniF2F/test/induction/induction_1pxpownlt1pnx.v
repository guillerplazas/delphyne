(* miniF2F problem: induction_1pxpownlt1pnx
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Show that for any real number $x$ and any natural number $n$, if $x > -1$, then
   $(1+nx)\leq (1+x)^n$.

   Informal proof:
   We show the result by induction on $n$. The result is trivial for $n=0$ or $n=1$. Let
   us assume the property is true in $n$.
   By the induction hypothesis we know that $(1+nx)\leq (1+x)^n$.
   Moreover, as $x > -1$, we have that $x \leq x (1 + x)^n$. The inequality is trivial
   if $x \geq 0$, and is also true if $x < 0$ as $-1 < x < 0 \implies 0 < (1 + x)^n <
   1$.
   So, $(1+nx) + x \leq (1+x)^n + x (1+x)^n$ and we have that $(1+(n+1)x) \leq
   (1+x)^(n+1)$, so the property is true in $n+1$.
   By induction, we have that the result is true for any natural number $n$.
*)

Require Import Reals.

Open Scope R_scope.

Theorem induction_1pxpownlt1pnx
    (x : R)
    (n : nat)
    (h₀ : -1 < x) :
    (1 + INR n * x) <= Rpower (1 + x) (INR n).

Proof.
Admitted.
