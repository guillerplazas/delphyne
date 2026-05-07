(* miniF2F problem: amc12b_2020_p21
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many positive integers $n$ satisfy $\dfrac{n+1000}{70} = \lfloor \sqrt{n}
   \rfloor?$(Recall that $\lfloor x\rfloor$ is the greatest integer not exceeding $x$.)

   $\textbf{(A) } 2 \qquad\textbf{(B) } 4 \qquad\textbf{(C) } 6 \qquad\textbf{(D) } 30
   \qquad\textbf{(E) } 32$ Show that it is \textbf{(C) }6.

   Informal proof:
   First notice that the graphs of $(n+1000)/70$ and $\sqrt[]{n}$ intersect at 2 points.
   Then, notice that $(n+1000)/70$ must be an integer, since it is equal to the floor of
   $n$. This means that n is congruent to $50 \pmod{70}$. 

   For the first intersection, testing the first few values of $n$ (adding $70$ to $n$
   each time and noticing the left side increases by $1$ each time) yields $\lfloor
   \sqrt{n} \rfloor=20$ and $\lfloor \sqrt{n} \rfloor=21$, so $n=400, 470$ respectively.
   Estimating from the graph can narrow down the other cases, being $\lfloor \sqrt{n}
   \rfloor=47$, $\lfloor \sqrt{n} \rfloor=48$, $\lfloor \sqrt{n} \rfloor=49$, $\lfloor
   \sqrt{n} \rfloor=50$, yielding $n=2290,2360,2430,2500$ respectively. This results in
   a total of 6 cases, for an answer of $\textbf{(C) }6$.
*)

Require Import Reals.
Require Import Rfunctions.
Require Import Sets.Ensembles.
Require Import Sets.Finite_sets.
Require Import ZArith.

Open Scope R_scope.

Theorem amc12b_2020_p21:
  let S := fun n:nat => 
    (0 < n)%nat /\ 
    exists k:Z, 
      (IZR k = (INR n + 1000) / 70) /\
      k = Z.of_nat (Z.to_nat (up (sqrt (INR n)) - 1)) in
  Finite nat S /\ cardinal nat S 6.

Proof.
Admitted.
