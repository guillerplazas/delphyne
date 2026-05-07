(* miniF2F problem: amc12a_2021_p18
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $f$ be a function defined on the set of positive rational numbers with the
   property that $f(a\cdot b)=f(a)+f(b)$ for all positive rational numbers $a$ and $b$.
   Suppose that $f$ also has the property that $f(p)=p$ for every prime number $p$. For
   which of the following numbers $x$ is $f(x)<0$?

   $\textbf{(A) }\frac{17}{32} \qquad \textbf{(B) }\frac{11}{16} \qquad \textbf{(C)
   }\frac79 \qquad \textbf{(D) }\frac76\qquad \textbf{(E) }\frac{25}{11}$ Show that it
   is \textbf{(E) }\frac{25}{11}.

   Informal proof:
   From the answer choices, note that
   $\begin{align*}
   f(25)&=f\left(\frac{25}{11}\cdot11\right) \\
   &=f\left(\frac{25}{11}\right)+f(11) \\
   &=f\left(\frac{25}{11}\right)+11.
   \end{align*}$
   On the other hand, we have
   $\begin{align*}
   f(25)&=f(5\cdot5) \\
   &=f(5)+f(5) \\
   &=5+5 \\
   &=10.
   \end{align*}$
   Equating the expressions for $f(25)$ produces $f\left(\frac{25}{11}\right)+11=10,$
   from which $f\left(\frac{25}{11}\right)=-1.$ Therefore, the answer is $\textbf{(E)
   }\frac{25}{11}.$

   <u><b>Remark</b></u>

   Similarly, we can find the outputs of $f$ at the inputs of the other answer choices:
   $\begin{alignat*}{10}
   &\textbf{(A)} \qquad && f\left(\frac{17}{32}\right) \quad && = \quad && 7 \\ 
   &\textbf{(B)} \qquad && f\left(\frac{11}{16}\right) \quad && = \quad && 3 \\ 
   &\textbf{(C)} \qquad && f\left(\frac{7}{9}\right) \quad && = \quad && 1 \\ 
   &\textbf{(D)} \qquad && f\left(\frac{7}{6}\right) \quad && = \quad && 2
   \end{alignat*}$
   Alternatively, refer to Solutions 2 and 4 for the full processes.

   ~Lemonie ~awesomediabrine
*)

Require Import Reals.
Require Import QArith.
Require Import Znumtheory.
From Stdlib Require Import Qreals.

Theorem amc12a_2021_p18
  (f : Q -> R)
  (hcompat : forall x y : Q, Qeq x y -> f x = f y)
  (h0 : forall x y : Q, (0 < x)%Q -> (0 < y)%Q -> f (Qmult x y) = Rplus (f x) (f y))
  (h1 : forall p : Z, prime p -> f (inject_Z p) = IZR p) :
  (f (Qmake 25 11) < 0)%R.

Proof.
Admitted.
