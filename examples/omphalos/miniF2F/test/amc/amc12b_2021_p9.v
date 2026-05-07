(* miniF2F problem: amc12b_2021_p9
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   What is the value of$\frac{\log_2 80}{\log_{40}2}-\frac{\log_2
   160}{\log_{20}2}?$$\textbf{(A) }0 \qquad \textbf{(B) }1 \qquad \textbf{(C) }\frac54
   \qquad \textbf{(D) }2 \qquad \textbf{(E) }\log_2 5$ Show that it is \text{(D)}.

   Informal proof:
   $\frac{\log_{2}{80}}{\log_{40}{2}}-\frac{\log_{2}{160}}{\log_{20}{2}}$

   Note that $\log_{40}{2}=\frac{1}{\log_{2}{40}}$, and similarly
   $\log_{20}{2}=\frac{1}{\log_{2}{20}}$

   $= \log_{2}{80}\cdot \log_{2}{40}-\log_{2}{160}\cdot \log_{2}{20}$

   $=(\log_{2}{4}+\log_{2}{20})(\log_{2}{2}+\log_{2}{20})-(\log_{2}{8}+\log_{2}{20})\log_{2}{20}$

   $=(2+\log_{2}{20})(1+\log_{2}{20})-(3+\log_{2}{20})\log_{2}{20}$

   Expanding,
   $2+2\log_{2}{20}+\log_{2}{20}+(\log_{2}{20})^2-3\log_{2}{20}-(\log_{2}{20})^2$

   All the log terms cancel, so the answer is $2\implies\text{(D)}$.
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2021_p9 :
  (ln 80 / ln 2) / (ln 2 / ln 40) - (ln 160 / ln 2) / (ln 2 / ln 20) = 2.
Proof.
Admitted.