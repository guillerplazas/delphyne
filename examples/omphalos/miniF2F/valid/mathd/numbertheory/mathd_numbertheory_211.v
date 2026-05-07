(* miniF2F problem: mathd_numbertheory_211
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many integers $n$ satisfy $0<n<60$ and $4n\equiv 2\pmod 6?$ Show that it is 20.

   Informal proof:
   The residue of $4n\pmod 6$ is determined by the residue of $n\pmod 6.$ We can build a
   table showing the possibilities: $$\begin{array}{r || c * 5 {| c}}
   n\pmod 6 & 0 & 1 & 2 & 3 & 4 & 5 \\
   \hline
   4n\pmod 6 & 0 & 4 & 2 & 0 & 4 & 2
   \end{array}$$As the table shows, $4n\equiv 2\pmod 6$ is true when $n\equiv 2$ or
   $n\equiv 5\pmod 6.$ Otherwise, it's false.

   So, our problem is to count all $n$ between $0$ and $60$ that leave a remainder of
   $2$ or $5$ modulo $6.$ These integers are $$2, 5, 8, 11, 14, 17, \ldots, 56,
   59.$$There are $20$ integers in this list.
*)

Require Import List.
Import ListNotations.
Require Import Arith.

Theorem mathd_numbertheory_211 :
  length (filter (fun n => (4 * n - 2) mod 6 =? 0) (List.seq 1 59)) = 20.

Proof.
Admitted.
