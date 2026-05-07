(* miniF2F problem: amc12a_2020_p21
   Split: valid
   Source: https://github.com/LLM4Rocq/miniF2F-rocq

   Informal statement:
   How many positive integers $n$ are there such that $n$ is a multiple of $5$, and the
   least common multiple of $5!$ and $n$ equals $5$ times the greatest common divisor of
   $10!$ and $n?$

   $\textbf{(A) } 12 \qquad \textbf{(B) } 24 \qquad \textbf{(C) } 36 \qquad \textbf{(D)
   } 48 \qquad \textbf{(E) } 72$ Show that it is \textbf{(D) } 48.

   Informal proof:
   We set up the following equation as the problem states:

   $$ \text{lcm}{(5!, n)} = 5\text{gcd}{(10!, n)}.$$

   Breaking each number into its prime factorization, we see that the equation becomes

   $$ \text{lcm}{(2^3\cdot 3 \cdot 5, n)} = 5\text{gcd}{(2^8\cdot 3^4 \cdot 5^2 \cdot 7,
   n)}.$$

   We can now determine the prime factorization of $n$. We know that its prime factors
   belong to the set $\{2, 3, 5, 7\}$, as no factor of $10!$ has $11$ in its prime
   factorization, nor anything greater. Next, we must find exactly how many different
   possibilities exist for each.

   There can be anywhere between $3$ and $8$ $2$'s and $1$ to $4$ $3$'s. However, since
   $n$ is a multiple of $5$, and we multiply the $\text{gcd}$ by $5$, there can only be
   $3$ $5$'s in $n$'s prime factorization. Finally, there can either $0$ or $1$ $7$'s.

   Thus, we can multiply the total possibilities of $n$'s factorization to determine the
   number of integers $n$ which satisfy the equation, giving us $6 \times 4 \times 1
   \times 2 = \textbf{(D) } 48$.
*)

Require Import Nat.
Require Import ZArith.
Require Import List.
Require Import ListSet.
Require Import Arith.


Fixpoint fact (n : nat) : nat :=
  match n with
  | 0 => 1
  | S n' => S n' * fact n'
  end.


Definition satisfies_condition (n : nat) : Prop :=
  (exists k : nat, n = k * 5) /\ 
  Nat.lcm (fact 5) n = 5 * Nat.gcd (fact 10) n.


Theorem amc12a_2020_p21 :
  exists (l : list nat),
    NoDup l /\
    (forall n : nat, In n l <-> satisfies_condition n) /\
    length l = 48.

Proof.
Admitted.
