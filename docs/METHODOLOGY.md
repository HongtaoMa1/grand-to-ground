# Grand-to-Ground (G2G)

**A practical methodology for AI-assisted research in the social sciences**

Rick Ma (Hongtao Ma) · 2026 · v1.0 — This document practices what it preaches: it was produced jointly by the author and AI research agents. The author supplied the vision, the taste, and the final say; the agents supplied literature reconnaissance, adversarial critique, and drafting.

## 1. The open space

In 2025–26, AI research systems came of age in the experimental sciences. Google's Co-Scientist orchestrates agents that generate, debate, rank, and evolve hypotheses — published in *Nature* in May 2026, with wet-lab validations. Sakana's AI Scientist has produced papers that passed peer review end to end. Both rest on one assumption: a laboratory, wet or computational, exists to close the loop.

Social science enjoys no such luxury. Its theories are built by deduction from assumptions at least as much as by induction from data. Its "experiments" are history: natural experiments, archives, observational datasets. And its hardest step — choosing the right question — is a matter of taste. The frontier systems therefore do not transfer directly, and the space remains open. G2G is a methodology for exactly that space: a single researcher, off-the-shelf AI agents, and a disciplined loop between grand ideas and identifiable questions.

## 2. Division of labor

The human brings divergent intuition (where to look), taste (which question is worth anyone's time), arbitration (which agent wins a dispute), and verification (no fact enters the record unchecked). The AI brings breadth: literature reconnaissance across fields, translation of prose into formal propositions, tireless deduction, adversarial critique, and bookkeeping.

This split follows the evidence, not ideology. The largest controlled comparison to date (Stanford, 100+ NLP researchers) found LLM-generated research ideas rated significantly *more novel* than experts' — and somewhat *less feasible*. So let AI supply novelty; let the human supply feasibility and own every choice.

## 3. The pipeline (P0–P8)

- **P0 Vision.** State the grand framework in plain language — hunches, end-state claims, and all. A grand narrative is unpublishable; it is also the best question generator you own.
- **P1 Reconnaissance.** Agents sweep the literature. The gate: if the field already holds your conclusion in deeper form, switch to learning mode — absorb it, then re-enter the loop standing on it. Where your interest collides with existing work is usually where innovation lives.
- **P2 Formalization.** Translate the narrative into propositions with operationalized terms — definitions someone could measure. Prefer borrowing the skeleton of an established model over inventing notation.
- **P3 Axiomatization.** Declare a Lakatosian *hard core* — the few assumptions the programme will protect — and a *protective belt* of auxiliary hypotheses that absorbs attacks. Every axiom must be fact-checked by the human before entering the core: a false "fact" planted there will be defended brilliantly forever after. Critics may attack the belt every round; attacks on the core are logged rather than adjudicated on the spot, and reviewed periodically — is the programme still producing novel predictions (progressive), or only patching itself (degenerating)?
- **P4 Conjecture.** Instruct an agent to nominate one piece of "common sense" as possibly false, and to guess where information is missing — guesses explicitly marked. The explored roads are crowded; the unexplored ones are mostly unexplored for lack of known information. Guessing it, visibly, is a legitimate move.
- **P5 Deduction.** A deducer agent derives consequences strictly inside the axioms — no hedging, no smuggling in new assumptions. First drafts will be banal; that is what the next stage is for.
- **P6 Tribunal.** Fresh-context critics with divided mandates: a *logic critic* (internal contradictions only), an *evidence critic* (conflicts with data and history; live search allowed), a *novelty critic* (has this been done — and better?). Two constraints are mandatory. *Anti-sycophancy:* each critic must file a minimum number of objections and is forbidden to endorse overall. *Fresh context per round:* agents sharing one long conversation converge; the entire point is that they must not.
- **P7 Grounding.** Each surviving proposition must answer three questions: What observable prediction does it make? What data could refute it? Has history already run the experiment? A claim nothing could refute is decoration, not research.
- **P8 Score, stop, remember.** Score the round on four axes — internal consistency, empirical compatibility, falsifiability, novelty. Stop on plateau (two rounds without improvement) or on budget. Write conclusion cards and a contradiction log to persistent memory; feed both back into P4. The memory, not any single conclusion, is the asset.

## 4. The convergence principle

The publishable — and monetizable — unit of social science is not the grand framework. It is the **identifiable small question**: one mechanism, formalized, that some dataset or natural experiment can actually answer. G2G therefore ends every cycle with a cut: extract the smallest fragment that survived the tribunal and can be identified in data, and develop it to completion. Solved fragments re-enter the framework as known conditions — and usually expose which neighboring parts of the grand story were immature. Grand → ground → grand again, one solved piece at a time. Hence the name.

## 5. Anti-dogma rules

Field experience adds four mechanical rules that keep the loop from ossifying around the researcher's pet concepts:

- **R1 Rotation.** Never use the same theoretical-framework family in two consecutive cycles. Concepts the researcher emphasizes are entry points, not mandates.
- **R2 No re-cutting.** A registered question may not be cut again; derived questions must name their parent and the new increment.
- **R3 Cross-level linkage.** Every accepted conclusion must state what it means for at least one other layer of the framework. A result that is elegant at one layer and meaningless to the others is void.
- **R4 Mechanism first.** Each cycle must propose at least one cross-level mechanism. Describing group differences in preferences is not a mechanism.

## 6. Failure modes and guardrails

**Agent sycophancy and convergence** → role constraints, objection quotas, fresh contexts. **A polluted hard core** → human fact-verification of every axiom — the single most dangerous failure, because the system will rationalize a false core beautifully. **Context drift in long loops** → external memory files; one round per context window. **Narrative overfitting** (everything "confirms" the story) → mandatory grounding; falsifiability scored every round. **Human rubber-stamping** → read the tribunal log, not just the conclusion card. AI proposes; the human disposes.

## 7. References

- Google DeepMind (2026). Co-Scientist: a multi-agent AI partner to accelerate research. *Nature* publication, May 2026.
- Sakana AI (2025–26). The AI Scientist-v2. arXiv:2504.08066.
- Korinek, A. (2025). AI Agents for Economic Research. NBER Working Paper 34202.
- Si, C., Yang, D., & Hashimoto, T. (2024). Can LLMs Generate Novel Research Ideas? arXiv:2409.04109.
- Lakatos, I. (1970). Falsification and the Methodology of Scientific Research Programmes. In *Criticism and the Growth of Knowledge*. Cambridge University Press.
