# Arbeitsplan Masterthesis:

**Arbeitstitel (vorläufig):** LLM-Assisted Automated Theorem Proving In Rocq
**Betreuer:** Jonathan Laurent
**Geplantes Abgabedatum:** 01.11.2026

---

## 1. Zusammenfassung / Abstract

Recent LLM-assisted theorem provers — most notably the Hilbert method, which achieves 99.2% on miniF2F by combining informal LLM reasoning with verifier feedback — have advanced rapidly, but progress is concentrated on Lean 4, leaving Rocq without competitive AI-assisted proving tools. This thesis adapts the Hilbert method to Rocq using Delphyne, a Python framework that cleanly separates proof strategy from search policy. We make two main contributions. First, we deliver a competent Rocq proving agent that runs entirely on API-accessible models — making it broadly usable and customizable without specialized hardware or fine-tuning — and evaluate it on miniF2F (final benchmark to be confirmed) against existing Rocq baselines. Second, we empirically evaluate Delphyne itself as an implementation platform, testing the hypothesis that its modular architecture yields an agent that is simpler, more scalable, and easier to customize than a standard pipeline, through a structured study of variations and extensions. Time permitting, we additionally develop a Delphyne coding assistant — a set of Delphyne skill and prompt files — that helps users author strategies and policies from natural-language descriptions. As a stretch goal, we target a workshop paper at a Rocq/Coq community venue.

---

## 2. Forschungsfrage & Motivation

### 2.1. Motivation

LLM-assisted automated theorem proving has seen remarkable recent progress. The Hilbert method (Chen et al., 2025) achieves 99.2% on the miniF2F benchmark by combining informal LLM reasoning with formal tactic generation and verifier feedback — but its published results focus on Lean 4, and the broader ATP community has largely concentrated its effort there.

Rocq (the successor to Coq) is a mature proof assistant with a large mathematical library (MathComp) and strong roots in formal software verification (CompCert, formalization of the Feit–Thompson theorem, etc.). Despite this, Rocq currently lacks state-of-the-art LLM-assisted proving tools comparable to what now exists for Lean 4. This thesis addresses that gap by delivering a competent Rocq proving agent. A key design goal is accessibility and customizability: the agent relies exclusively on API-accessible models, so that any researcher or practitioner can run, adapt, and extend it without specialized hardware, fine-tuning infrastructure, or deep framework knowledge.

Beyond delivering a Rocq agent, this thesis also investigates whether Delphyne is the right platform on which to build it. Delphyne is a Python framework for composable, search-based LLM pipelines that cleanly separates proof strategy specification from search policy. Our hypothesis is that this separation of concerns makes the implementation simpler, more scalable, and easier to customize than a monolithic pipeline approach. The thesis treats this as an explicit research claim, to be confirmed empirically through a structured study of concrete variations and extensions — for example, swapping inference policies, adjusting the search budget, or adding a new tactic generator — and measuring how localized each modification is.

The secondary scope follows the same theme: a Delphyne coding assistant that lowers the entry barrier for new Delphyne users. Concretely, this is a collection of Delphyne skill and prompt files that help authors translate natural-language descriptions into working strategies and policies, and may require small contributions to Delphyne itself (e.g., improved CLI demo feedback) to better support agentic workflows.

### 2.2. Forschungsfrage

> **Zentrale Forschungsfrage (1):** Can the Hilbert method for hybrid informal/formal LLM-assisted automated theorem proving be successfully adapted to the Rocq proof assistant, and what performance does the resulting system achieve on standard ATP benchmarks? Does relying exclusively on API-accessible models yield a system that is accessible and customizable enough for the broader Rocq community?

> **Zentrale Forschungsfrage (2):** Does implementing a Hilbert-style Rocq proving agent in Delphyne yield a system that is measurably simpler to implement, more scalable, and easier to customize and extend than a comparable monolithic pipeline — and can this be confirmed through concrete ablations and extensions of the agent?


---

## 3. Messbare Erfolgskriterien (Evaluation)

1. **Core implementation:** A working end-to-end Delphyne pipeline that applies the Hilbert method to Rocq — comprising an informal reasoning component (LLM proof sketches), a formalization component (sketch → Rocq tactics), and a verifier feedback loop (error messages → iterative refinement). The agent runs exclusively on API-accessible models with no local fine-tuning required.

2. **Benchmark performance:** A measurable proof pass rate on miniF2F problems formalized in Rocq (preliminary evaluation target), with the final benchmark to be confirmed with the advisor. Results are compared against any existing Rocq/Coq ATP baselines (e.g., CoqHammer, Tactician).

3. **Non-trivial generalization:** The system solves problems that require multi-step reasoning, demonstrating that the hybrid approach scales beyond trivial one-tactic goals.

4. **Delphyne value validation:** A structured study of concrete variations and extensions — e.g., swapping inference policies, adjusting search budget, adding a new tactic generator, extending the retriever — demonstrating that each modification is localized and requires minimal change to other components. This empirically supports (or qualifies) the claims that Delphyne yields a simpler, more scalable, and more customizable implementation.

5. **Secondary scope (time-permitting):** A working Delphyne coding assistant for Rocq: concretely, a set of Delphyne skill and prompt files that help users produce Delphyne strategy and policy code from natural-language descriptions, evaluated on a representative set of example tasks. May include a small contribution to Delphyne itself (e.g., improved CLI demo feedback to better support agentic workflows).

6. **Stretch goal — workshop paper:** A workshop paper submission to a Rocq/Coq community venue (e.g., the Coq Workshop at ITP or POPL), presenting the agent design, Delphyne platform evaluation, and benchmark results.

---

## 4. Detaillierter Wöchentlicher Arbeitsplan

*(Ein realistischer Zeitplan ist entscheidend, um pünktlich und stressfrei fertig zu werden. Dieser Plan sollte Implementierung, Schreiben und Recherche von Anfang an integrieren.)*

| Woche | Datum       | Hauptziel Implementierung/Aufgabe     | Hauptziel Schreiben                     |
|:------|:------------|:--------------------------------------|:----------------------------------------|
| 1     | 27.04–03.05 | Literature review: Hilbert paper, related ATP work; set up dev environment (Rocq + Delphyne) | Draft introduction outline |
| 2     | 04.05–10.05 | Study Hilbert architecture and Lean 4 implementation in detail. Get familiar with ROCQ - Delphyne intersection. | Background chapter: Rocq tactic system and proof state |
| 3     | 11.05–17.05 | Deep dive into Delphyne internals (strategies, policies, demos) applied to Hilbert and ROCQ approach| Background chapter: ATP landscape and related systems |
| 4     | 18.05–24.05 | Analyse existing Rocq ATP tools (CoqHammer, Tactician, etc.) - Pipeline implementation? | Background chapter: describe the Hilbert method |
| 5     | 25.05–31.05 | Understand miniF2F structure and existing Rocq formalisations | Finish introduction chapter draft |
| 6     | 01.06–07.06 | Implement Rocq interface layer (SerAPI / coq-lsp: proof state + tactic execution) | Chapter 3 (Architecture): outline |
| 7     | 08.06–14.06 | Implement Delphyne strategy for tactic generation + proof-state parsing | Chapter 3 (Architecture): draft |
| 8     | 15.06–21.06 | Implement informal reasoning component (LLM prompt design for proof sketches) | Write methodology section |
| 9     | 22.06–28.06 | Implement formalisation component (sketch → Rocq tactics) | Continue methodology section |
| 10    | 29.06–05.07 | Implement verifier feedback loop (error analysis → informal reasoner) | Chapter 4 (Implementation): draft |
| 11    | 06.07–12.07 | Implement theorem/lemma retriever for Rocq/MathComp libraries | Continue Chapter 4 |
| 12    | 13.07–19.07 | End-to-end integration testing on simple Rocq examples; fix bugs | Finish Chapter 4 |
| 13    | 20.07–26.07 | Run system on miniF2F subset; measure pass rates; identify failure modes | Chapter 5 (Evaluation): outline |
| 14    | 27.07–02.08 | Tune prompts, policies, and search strategy based on results | Chapter 5 (Evaluation): draft |
| 15    | 03.08–09.08 | Full benchmark run (miniF2F or final decided benchmark); run Delphyne variations/extensions study (swap policies, adjust search budget, add tactic generator) | Write out evaluation chapter (benchmark + Delphyne value validation) |
| 16    | 10.08–16.08 | Analyse variation results; compare against baselines; document effort-per-change | Write discussion section |
| 17    | 17.08–23.08 | Finalise evaluation; document system weaknesses and limitations | Write conclusions and limitations |
| 18    | 24.08–30.08 | Design Delphyne coding assistant: define skill + prompt file structure; identify any required Delphyne CLI features (e.g., improved demo feedback) | Introduce secondary scope (chapter outline) |
| 19    | 31.08–06.09 | Implement skill + prompt files for coding assistant; implement any needed Delphyne CLI features | Describe coding assistant implementation |
| 20    | 07.09–13.09 | Evaluate coding assistant on representative example tasks | Write secondary scope results |
| 21    | 14.09–20.09 | **(Stretch) Workshop paper draft:** write up agent design + Delphyne evaluation + benchmark results for Rocq/Coq workshop venue | First complete thesis draft; send to advisor |
| 22    | 21.09–27.09 | Incorporate advisor feedback (round 1); **(Stretch)** revise workshop paper draft | Revise and polish all chapters |
| 23    | 28.09–04.10 | Second revision pass; **(Stretch)** finalize and submit workshop paper | Refine writing and figures |
| 24    | 05.10–11.10 | Buffer / minor experiments if needed | Write Abstract (Section 1) |
| 25    | 12.10–18.10 | —                                     | Proofreading; incorporate advisor feedback (round 2) |
| 26    | 19.10–25.10 | —                                     | Final copy-edit, formatting, bibliography check; send draft to advisor |
| 27    | 26.10–01.11 | —                                     | Address final comments; submit by 01.11.2026 |
