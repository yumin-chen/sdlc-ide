# Theory: Multi-Perspective Empathic Mediation (MPEM)

**Core idea:** model interactions as mediation problems where the assistant’s job is to *represent, translate, and reconcile* multiple mental models (perspectives) while preserving safety, autonomy, and accountability.

MPEM has three mutually reinforcing axioms:

1. **Perspective Fidelity:** the assistant must generate faithful, plausible internal models for each stakeholder (cognitive level, goals, constraints, emotional state).
2. **Translational Accuracy:** the assistant should produce translations between perspectives that preserve intent and plausible emotional valence, not moralize or invent motivations.
3. **Human-in-the-Loop Authority:** the assistant’s outputs are proposals; humans retain decision and escalation control, and the system must present uncertainty/confidence and reasons.

From those axioms follow the main objectives:

* Build **theory of mind** modules (age-appropriate cognitive models, biases, responsibilities).
* Provide **reframe & script utilities** (e.g., “explain to child why X” / “explain to parent how child sees X”).
* Measure **alignment & safety** (was the translation helpful? did it escalate harm?).

---

# System Architecture (high level)

A pipeline you can implement in an LLM product:

1. **Input** — Conversation context, user role (parent/child/teacher), explicit goals (reassure, set boundary, de-escalate), optional child age, culture, prior history.
2. **Perception & Annotation Layer**

   * Affective analysis (explicit text cues; optional audio/vision signals).
   * Intent extraction (what does the speaker want?).
   * Safety triage (self-harm, abuse, illegal acts).
3. **Perspective Modeling Module**

   * **Profiles:** short dynamic personas (cognitive level, priorities, vocabulary, likely misconceptions).
   * **Theory-of-Mind (ToM) generator:** for each actor, a short explanation of beliefs, emotions, constraints, and likely misperceptions.
4. **Translation Engine**

   * **Reframing policies:** rules + LLM templates to translate content across cognitive levels (e.g., simplify explanation for 8-yr-old; translate teen’s sarcasm for parent).
   * **Message variants:** empathic, factual, boundary-setting, motivation-framing.
   * **Safety constraints:** must not produce coaching for evading supervision, etc.
5. **Decision & Action Planner**

   * Ranks candidate messages by estimated utility (e.g., measured by simulated rollouts or learned reward models).
   * Adds confidence, rationale, and suggested next actions (e.g., “pause conversation,” “call professional”).
6. **Human Interface**

   * Presents choices with short rationales and editable text.
   * Clear “why this” explanation and estimated risk.
7. **Feedback Loop & Memory**

   * Records which suggestion was used and outcome labels (user-provided or inferred).
   * Updates profiles and translation heuristics.

---

# Modeling components (concrete)

**1. Persona template (for each actor)**

* `role`: parent / child / teen / teacher
* `age_range`: 6–8, 9–12, 13–17, adult
* `cognitive_features`: e.g., “concrete thinking; limited long-term perspective”
* `emotional_triggers`: common triggers and de-escalation strategies
* `primary_goals`: safety, autonomy, fairness, etc.

**2. ToM snippet (auto-generated)**

* `Beliefs`: short bullet list of what they likely believe now
* `Misconceptions`: likely mistakes in reasoning
* `Intent`: what they are trying to accomplish
* `Recommended tone`: direct, playful, firm-with-empathy

**3. Reframing templates**

* For child: “Short explanation + 2 examples + one question to check understanding”
* For parent: “1-sentence summary of child’s POV + why they feel this way + 2 practical next steps”
* For reconciliation: “Common ground + boundary + empathy statement”

**4. Safety rules**

* Hard constraints: never provide medical/legal diagnostics; reportable harm triggers escalation flow.
* Soft constraints: avoid shaming language; prefer autonomy-supportive phrasing.

---

# Prompt engineering examples

(You can embed these into the Translation Engine.)

**System prompt (core):**

```
You are a mediating assistant. Given context, generate:
1) a 3-line Theory-of-Mind for each actor (beliefs, emotions, goals),
2) three candidate messages: one for actor A framed for actor B (short, age-appropriate), one de-escalation script, and one boundary script.
Always include a short rationale and a confidence score (0–1). Follow safety rules.
```

**Example parent→child prompt template:**

```
Context: [text]
Child age: [10]
Goal: parent wants to explain why curfew is 9pm after an argument.

Produce:
- Child ToM (3 bullets)
- Message for child (<= 60 words, simple language, includes "because" + example)
- Follow-up question parent can ask to check understanding
```

**Example child→parent translation:**

```
Context: [text]
Child age: [15]
Tone: nonjudgmental. Explain teen's perspective in 2 sentences, include likely misperception parent has.
```

---

# Learning & Personalization

* **Cold start:** default developmental heuristics (Piaget, Erikson, common behavioral science).
* **Personalization:** lightweight user profile (communication preferences, prior successful phrases), stored as editable memory.
* **Online learning:** collect outcome signals (did user send the suggestion? user rating of help; turn success labels) and update ranking model.

---

# Evaluation: metrics & experiments

Design both offline and online evaluations.

**Automatic metrics**

* *Perspective fidelity score*: human raters judge how accurately generated ToM matches a vignette.
* *Readability / grade level*: Flesch-Kincaid for child messages.
* *Safety pass rate*: percent of outputs violating hard constraints.

**Human evaluations**

* *Parent usefulness*: Likert scores on whether the suggestion helped the conversation.
* *Child comprehension*: measure via quizzes or behavior (did child follow instruction?).
* *Longitudinal trust*: retention of users over repeated interactions.

**A/B tests**

* Compare baseline advice (no ToM) vs MPEM suggestions on real outcomes: escalation rate, satisfaction, de-escalation time.

---

# Example (concrete)

User input (parent):

> “My 14-yr-old slammed the door, said I don’t understand, and refuses to come down for dinner. I feel disrespected. What should I say?”

System output (compressed):

* **Child ToM:** feels cornered; wants autonomy; may be embarrassed to talk in front of siblings.
* **Suggested message (for parent to send):**
  “I’m not trying to control you — I want to know you’re okay. I noticed you slammed the door and seem upset. When you’re ready, I’d like 10 minutes to hear what’s going on.”
* **Rationale:** acknowledges emotion, reduces threat, offers time-limited request for talk. Confidence 0.8.
* **Next step:** If child refuses > wait 30min then send a brief check-in: “Can we talk in private later tonight?”

---

# Safety, ethics, and governance

* **Transparency:** always show rationale and confidence; mark system suggestions as assistant proposals.
* **Consent & privacy:** store only what user agrees to; children’s data laws (COPPA, GDPR-K) must be followed.
* **Avoid manipulation:** do not craft messages intended to coerce, gaslight, or bypass parental/legal safeguards.
* **Escalation:** implement robust triage for threats (harm, abuse) and route to human moderators / emergency services per policy.

---

# Implementation roadmap (practical steps)

1. Build persona & ToM schema and seed with developmental heuristics.
2. Create prompt templates and safety filters; integrate with base LLM.
3. Implement simple UI that surfaces: (a) ToM summaries, (b) 3 message variants, (c) rationale & confidence.
4. Run small usability study with consenting adult users and simulated child vignettes.
5. Collect outcomes & iterate: refine persona templates and ranking model.
6. Add personalization and automated A/B tests for metrics above.

---

# Failures to watch for

* Over-fitting to stereotypes (age/gender/culture) — incorporate cultural adaptation and explicit user overrides.
* Hallucinated “child motivations” — always present as plausible hypotheses, not facts.
* Overreliance on the assistant — preserve human decision authority and include friction where necessary.

---

# Quick checklist you can copy

* [ ] Persona schema defined (age, cognitive, triggers)
* [ ] Safety triage rules implemented
* [ ] 3-variant message generator built (empathy/factual/boundary)
* [ ] Explainability UI (ToM + rationale + confidence)
* [ ] Logging + user feedback loop for learning
* [ ] Human evaluation plan + metrics

---

If you want, I can:

* draft the exact JSON schema for persona/ToM and sample seed values for ages 6–17, **or**
* write the initial prompt templates and safety rules as ready-to-use prompts for fine-tuning/reranking.

Which would be most useful next?
