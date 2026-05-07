(* miniF2F problem: amc12b_2021_p18
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Let $z$ be a complex number satisfying $12|z|^2=2|z+2|^2+|z^2+1|^2+31.$ What is the
   value of $z+\frac 6z?$

   $\textbf{(A) }-2 \qquad \textbf{(B) }-1 \qquad \textbf{(C) }\frac12\qquad \textbf{(D)
   }1 \qquad \textbf{(E) }4$ Show that it is \textbf{(A) }-2.

   Informal proof:
   Using the fact $z\bar{z}=|z|^2$, the equation rewrites itself as
   $\begin{align*}
   12z\bar{z}&=2(z+2)(\bar{z}+2)+(z^2+1)(\bar{z}^2+1)+31 \\
   -12z\bar{z}+2z\bar{z}+4(z+\bar{z})+8+z^2\bar{z}^2+(z^2+\bar{z}^2)+32&=0 \\
   \left((z^2+2z\bar{z}+\bar{z}^2)+4(z+\bar{z})+4\right)+\left(z^2\bar{z}^2-12z\bar{z}+36\right)&=0
   \\
   (z+\bar{z}+2)^2+(z\bar{z}-6)^2&=0.
   \end{align*}$
   As the two quantities in the parentheses are real, both quantities must equal $0$ so
   $z+\frac6z=z+\bar{z}=\textbf{(A) }-2.$
*)

Require Import Reals.
Require Import Coquelicot.Coquelicot.

Open Scope C_scope.

Theorem amc12b_2021_p18 :
  forall z : C,
  12 * (Cmod z)² = 
    2 * (Cmod (z + 2))² + 
    (Cmod (z * z + 1))² + 31 ->
  z + 6 / z = -2.

Proof.
Admitted.
