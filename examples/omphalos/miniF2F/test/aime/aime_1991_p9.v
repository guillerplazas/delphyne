(* miniF2F problem: aime_1991_p9
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Suppose that $\sec x+\tan x=\frac{22}7$ and that $\csc x+\cot x=\frac mn,$ where
   $\frac mn$ is in lowest terms.  Find $m+n^{}_{}.$ Show that it is 044.

   Informal proof:
   Use the two [[Trigonometric identities#Pythagorean Identities|trigonometric
   Pythagorean identities]] $1 + \tan^2 x = \sec^2 x$ and $1 + \cot^2 x = \csc^2 x$. 

   If we square the given $\sec x = \frac{22}{7} - \tan x$, we find that 

   $\begin{align*}
   \sec^2 x &= \left(\frac{22}7\right)^2 - 2\left(\frac{22}7\right)\tan x + \tan^2 x \\
   1 &= \left(\frac{22}7\right)^2 - \frac{44}7 \tan x \end{align*}$

   This yields $\tan x = \frac{435}{308}$. 

   Let $y = \frac mn$. Then squaring, 

   $\csc^2 x = (y - \cot x)^2 \Longrightarrow 1 = y^2 - 2y\cot x.$ 

   Substituting $\cot x = \frac{1}{\tan x} = \frac{308}{435}$ yields a [[quadratic
   equation]]: $0 = 435y^2 - 616y - 435 = (15y - 29)(29y + 15)$. It turns out that only
   the [[positive]] root will work, so the value of $y = \frac{29}{15}$ and $m + n =
   044$.

   Note: The problem is much easier computed if we consider what $\sec (x)$ is, then
   find the relationship between $\sin( x)$ and $cos (x)$ (using $\tan (x) =
   \frac{435}{308}$, and then computing $\csc x + \cot x$ using $1/\sin x$ and then the
   reciprocal of $\tan x$.
*)

Require Import Reals.
Require Import QArith.
Require Import Coq.QArith.Qround.
Require Import ZArith.

Open Scope R_scope.

Theorem aime_1991_p9 :
  forall (x : R),
    cos x <> 0 ->
    sin x <> 0 ->
    (1 / cos x + tan x = 22 / 7)%R ->
    (exists p q : Z, (0 < q)%Z /\ Z.gcd p q = 1%Z /\
      (1 / sin x + 1 / tan x = IZR p / IZR q)%R /\
      (p + q)%Z = 44%Z).

Proof.
Admitted.
