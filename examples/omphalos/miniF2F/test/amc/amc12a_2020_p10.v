(* miniF2F problem: amc12a_2020_p10
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   There is a unique positive integer $n$ such that$\log_2{(\log_{16}{n})} =
   \log_4{(\log_4{n})}.$What is the sum of the digits of $n?$

   $\textbf{(A) } 4 \qquad \textbf{(B) } 7 \qquad \textbf{(C) } 8 \qquad \textbf{(D) }
   11 \qquad \textbf{(E) } 13$ Show that it is \textbf{(E) } 13.

   Informal proof:
   Any logarithm in the form $\log_{a^b} c = \frac{1}{b} \log_a c.$ This can be proved
   easily by using change of base formula to base $a.$

   So, the original equation $\log_2{(\log_{2^4}{n})} = \log_{2^2}{(\log_{2^2}{n})}$
   becomes $\log_2\left({\frac{1}{4}\log_{2}{n}}\right) =
   \frac{1}{2}\log_2\left({\frac{1}{2}\log_2{n}}\right).$
   Using log property of addition, we expand both sides and then simplify:
   $\begin{align*}
   \log_2{\frac{1}{4}}+\log_2{(\log_{2}{n}}) &= \frac{1}{2}\left[\log_2{\frac{1}{2}}
   +\log_{2}{(\log_2{n})}\right] \\
   \log_2{\frac{1}{4}}+\log_2{(\log_{2}{n}}) &= \frac{1}{2}\left[-1
   +\log_{2}{(\log_2{n})}\right] \\
   -2+\log_2{(\log_{2}{n}}) &= -\frac{1}{2}+ \frac{1}{2}(\log_{2}{(\log_2{n})}).
   \end{align*}$
   Subtracting $\frac{1}{2}(\log_{2}{(\log_2{n})})$ from both sides and adding $2$ to
   both sides gives us $\frac{1}{2}(\log_{2}{(\log_2{n})}) = \frac{3}{2}.$
   Multiplying by $2,$ exponentiating, and simplifying gives us
   $\begin{align*}
   \log_{2}{(\log_2{n})} &= 3 \\
   \log_2{n}&=8 \\
   n&=256.
   \end{align*}$
   Adding the digits together, we have $2+5+6=\textbf{(E) } 13.$ 
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.
Require Import ZArith.
Require Import List.
Require Import Nat.

Open Scope R_scope.

Definition log_base (b x : R) : R := ln x / ln b.

Fixpoint sum_digits_aux (fuel n acc: nat) {struct fuel} : nat :=
  match fuel with
  | 0 => acc
  | S fuel' => match n with
               | 0 => acc
               | _ => sum_digits_aux fuel' (n / 10) (acc + (n mod 10))
               end
  end.

Definition sum_digits (n: nat) : nat := sum_digits_aux (S n) n 0.

Theorem amc12a_2020_p10 :
  exists! n : nat,
  (n > 0)%nat /\
  log_base 2 (log_base 16 (INR n)) = log_base 4 (log_base 4 (INR n)) /\
  sum_digits n = (13%nat).


Proof.
Admitted.
