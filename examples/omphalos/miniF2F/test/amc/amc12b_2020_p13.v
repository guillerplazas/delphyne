(* miniF2F problem: amc12b_2020_p13
   Split: test
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   Which of the following is the value of $\sqrt{\log_2{6}+\log_3{6}}?$

   $\textbf{(A) } 1 \qquad\textbf{(B) } \sqrt{\log_5{6}} \qquad\textbf{(C) } 2
   \qquad\textbf{(D) } \sqrt{\log_2{3}}+\sqrt{\log_3{2}} \qquad\textbf{(E) }
   \sqrt{\log_2{6}}+\sqrt{\log_3{6}}$ Show that it is \textbf{(D) }
   \sqrt{\log_2{3}}+\sqrt{\log_3{2}}.

   Informal proof:
   Recall that:
   <ol style=''margin-left: 1.5em;''>
   <li>$\log_b{(uv)}=\log_b u + \log_b v.$</li><p>
   <li>$\log_b u\cdot\log_u b=1.$</li><p>
   </ol>
   We use these properties of logarithms to rewrite the original expression:
   $\begin{align*}
   \sqrt{\log_2{6}+\log_3{6}}&=\sqrt{(\log_2{2}+\log_2{3})+(\log_3{2}+\log_3{3})} \\
   &=\sqrt{2+\log_2{3}+\log_3{2}} \\
   &=\sqrt{\left(\sqrt{\log_2{3}}+\sqrt{\log_3{2}}\right)^2} \\
   &=\textbf{(D) } \sqrt{\log_2{3}}+\sqrt{\log_3{2}}.
   \end{align*}$
*)

Require Import Reals.
Open Scope R_scope.

Theorem amc12b_2020_p13:
  sqrt ((ln 6 / ln 2) + (ln 6 / ln 3)) = sqrt (ln 3 / ln 2) + sqrt (ln 2 / ln 3).
Proof.
Admitted.