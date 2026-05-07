(* miniF2F problem: amc12a_2020_p9
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many solutions does the equation $\tan(2x)=\cos(\tfrac{x}{2})$ have on the
   interval $[0,2\pi]?$

   $ \textbf{(A)}\ 1\qquad\textbf{(B)}\ 2\qquad\textbf{(C)}\ 3\qquad\textbf{(D)}\
   4\qquad\textbf{(E)}\ 5 $ Show that it is \textbf{(E)}\ 5.

   Informal proof:
   We count the intersections of the graphs of $y=\tan(2x)$ and $y=\cos\left(\frac
   x2\right):$
   <ol style=''margin-left: 1.5em;''>
   <li>The graph of $y=\tan(2x)$ has a period of $\frac{\pi}{2},$ asymptotes at
   $x=\frac{\pi}{4}+\frac{k\pi}{2},$ and zeros at $x=\frac{k\pi}{2}$ for some integer
   $k.$ <p>
   On the interval $[0,2\pi],$ the graph has five branches:
   $\biggl[0,\frac{\pi}{4}\biggr),\left(\frac{\pi}{4},\frac{3\pi}{4}\right),\left(\frac{3\pi}{4},\frac{5\pi}{4}\right),\left(\frac{5\pi}{4},\frac{7\pi}{4}\right),\left(\frac{7\pi}{4},2\pi\right].$
   Note that $\tan(2x)\in[0,\infty)$ for the first branch, $\tan(2x)\in(-\infty,\infty)$
   for the three middle branches, and $\tan(2x)\in(-\infty,0]$ for the last branch.
   Moreover, all branches are strictly increasing.
   </li><p>
   <li>The graph of $y=\cos\left(\frac x2\right)$ has a period of $4\pi$ and zeros at
   $x=\pi+2k\pi$ for some integer $k.$ <p>
   On the interval $[0,2\pi],$ note that $\cos\left(\frac x2\right)\in[-1,1].$ Moreover,
   the graph is strictly decreasing.</li><p>
   </ol>
   The graphs of $y=\tan(2x)$ and $y=\cos\left(\frac x2\right)$ intersect once on each
   of the five branches of $y=\tan(2x),$ as shown below:

   Therefore, the answer is $\textbf{(E)}\ 5.$
*)

Require Import Reals.
Require Import Sets.Ensembles.
Require Import Sets.Finite_sets.

Open Scope R_scope.

Definition solution_set : Ensemble R :=
  fun x => 0 <= x /\ x <= 2 * PI /\ tan (2 * x) = cos (x / 2).

Theorem amc12a_2020_p9 :
  exists (S : Ensemble R),
    Same_set R S solution_set /\
    Finite R S /\
    cardinal R S 5.

Proof.
Admitted.
