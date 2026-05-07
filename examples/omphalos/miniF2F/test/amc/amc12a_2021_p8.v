(* miniF2F problem: amc12a_2021_p8
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   A sequence of numbers is defined by $D_0=0,D_1=0,D_2=1$ and $D_n=D_{n-1}+D_{n-3}$ for
   $n\ge 3$. What are the parities (evenness or oddness) of the triple of numbers
   $(D_{2021},D_{2022},D_{2023})$, where $E$ denotes even and $O$ denotes odd?

   $\textbf{(A) }(O,E,O) \qquad \textbf{(B) }(E,E,O) \qquad \textbf{(C) }(E,O,E) \qquad
   \textbf{(D) }(O,O,E) \qquad \textbf{(E) }(O,O,O)$ Show that it is \textbf{(C)
   }(E,O,E).

   Informal proof:
   We construct the following table:
   $\begin{array}{c||c|c|c|c|c|c|c|c|c|c|c}   
   &&&&&&&&&&& \\ [-2.5ex]
   \textbf{Term}
   &\boldsymbol{D_0}&\boldsymbol{D_1}&\boldsymbol{D_2}&\boldsymbol{D_3}&\boldsymbol{D_4}&\boldsymbol{D_5}&\boldsymbol{D_6}&\boldsymbol{D_7}&\boldsymbol{D_8}&\boldsymbol{D_9}&\boldsymbol{\cdots}
   \\ 
   \hline \hline
   &&&&&&&&&&& \\ [-2.25ex]
   \textbf{Value} & 0&0&1&1&1&2&3&4&6&9&\cdots \\ \hline  
   &&&&&&&&&&& \\ [-2.25ex]
   \textbf{Parity} & E&E&O&O&O&E&O&E&E&O&\cdots
   \end{array}$
   Note that $(D_7,D_8,D_9)$ and $(D_0,D_1,D_2)$ have the same parities, so the parity
   is periodic with period $7.$ Since the remainders of
   $(2021\div7,2022\div7,2023\div7)$ are $(5,6,7),$ we conclude that
   $(D_{2021},D_{2022},D_{2023})$ and $(D_5,D_6,D_7)$ have the same parities, namely
   $\textbf{(C) }(E,O,E).$
*)

Require Import Arith.

Theorem amc12a_2021_p8 :
  forall (d : nat -> nat),
    d 0 = 0 ->
    d 1 = 0 ->
    d 2 = 1 ->
    (forall n : nat, n >= 3 -> d n = d (n-1) + d (n-3)) ->
    (Nat.even (d 2021)) = true /\
    (Nat.even (d 2022)) = false /\
    (Nat.even (d 2023)) = true.

Proof.
Admitted.
