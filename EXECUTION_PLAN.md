# Divan-e Kabir Translation Project: Execution Plan

**Version**: 1.0 (Draft for Review)
**Date**: January 2026
**Author**: Hasnain Zaidi + Claude

---

## 1. Project Vision

Create an open-source, scholarly English translation of Rumi's complete Divan-e Kabir (~3,229 ghazals, ~44,000 verses) using a multi-agent LLM architecture that:

1. **Preserves Islamic and Sufi context** (following Omid Safi's approach)
2. **Achieves both accuracy and poetic quality** (bridging the Nicholson/Arberry vs. Barks gap)
3. **Enables community contribution and improvement**
4. **Demonstrates what LLMs make newly possible** in literary translation

---

## 2. Translation Philosophy

### 2.1 The Problem We're Solving

There's a gap in existing Rumi translations:

| Approach | Examples | Strength | Weakness |
|----------|----------|----------|----------|
| **Victorian Scholarly** | Nicholson, Arberry | Accurate, preserves context | Dry, archaic, unpoetic |
| **Popular/Versions** | Barks, Ladinsky | Accessible, poetic | Strips Islamic context, often inaccurate |
| **Modern Scholarly** | Mojaddedi, Lewis | Accurate + readable | Limited to Masnavi, not full Divan |

**Our target**: Accuracy of Arberry + Islamic context of Safi + accessibility of modern English

### 2.2 Omid Safi's Principles (Our North Star)

Based on research into Safi's *Radical Love* and public statements:

1. **Never strip Islamic references**
   - "Rumi's poetry is among the most Quranic of Islamic literatures"
   - Keep salat, ruku', sajda, Hajj, Quran, hadith explicit
   - Don't universalize "the Beloved" into generic spirituality

2. **Preserve Sufi technical vocabulary**
   - fana (annihilation), baqa (subsistence), sama' (spiritual audition)
   - These terms have specific meanings; glossing them loses precision

3. **Make contemporary English, not Victorian**
   - Use everyday language where possible
   - Safi example: titling a poem "Love is the GPS" to convey guidance metaphor

4. **Keep the passion and urgency**
   - Rumi is intense, ecstatic, intimate
   - Don't cool him down into polite spirituality

### 2.3 Concrete Translation Examples

**The "Kiss the Ground" Test Case**

| Version | Translation | Assessment |
|---------|-------------|------------|
| **Barks** | "Let the beauty we love be what we do. There are hundreds of ways to kiss the ground." | ❌ Strips Islamic prayer context entirely |
| **Accurate** | "There are one hundred kinds of prayers and prostrations (ruku' and sajda) when one faces their beloved's beauty as they pray." | ✅ Preserves namaz, ruku', sujud |

**Our approach**: The accurate version, but refined for English flow without losing the specificity.

---

## 3. Multi-Agent Architecture

### 3.1 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRANSLATION PIPELINE                               │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
│  │ ANALYZER │───▶│TRANSLATOR│───▶│ STYLIST  │───▶│    QA    │───▶│OUTPUT │ │
│  │          │    │          │    │          │    │          │    │       │ │
│  │ Pass 1   │    │ Pass 2   │    │ Pass 3   │    │ Pass 4   │    │       │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └───────┘ │
│       │                                               │                     │
│       └───────────────────────────────────────────────┘                     │
│                     (Analysis feeds into QA)                                │
└─────────────────────────────────────────────────────────────────────────────┘

                              BATCH CONSISTENCY
                    ┌──────────────────────────────────┐
                    │  Runs periodically across corpus │
                    │  - Terminology drift detection   │
                    │  - Voice consistency check       │
                    │  - Cross-reference validation    │
                    └──────────────────────────────────┘
```

### 3.2 Pass Descriptions

#### Pass 1: Analyzer
**Purpose**: Deep understanding before translation
**Model**: Claude Sonnet (cost-effective for analysis)
**Input**: Persian text + metadata (meter, rhyme)
**Output**: Structured analysis JSON

```json
{
  "grammatical_structure": "...",
  "quranic_allusions": [
    {"phrase": "...", "reference": "Quran 50:16", "meaning": "..."}
  ],
  "hadith_references": [...],
  "sufi_terminology": [
    {"term": "فنا", "transliteration": "fana", "meaning": "annihilation of ego in divine"}
  ],
  "ambiguities": [
    {"phrase": "یار", "possible_readings": ["God", "Shams", "human beloved"]}
  ],
  "wordplay": [
    {"word": "هوا", "meanings": ["air", "desire"], "note": "pun on physical/spiritual"}
  ],
  "meter_effects": "The hazaj meter creates urgency...",
  "difficult_constructions": [...]
}
```

#### Pass 2: Translator
**Purpose**: Accurate literal translation
**Model**: Claude Sonnet
**Input**: Persian text + Pass 1 analysis
**Output**: Literal translation with uncertainty markers

**Key instructions**:
- Use the terminology glossary consistently
- Mark uncertain translations with [?]
- Preserve hemistich structure
- Don't attempt poetry yet—prioritize accuracy
- Flag where multiple readings exist

#### Pass 3: Stylist
**Purpose**: Make it sound like Rumi
**Model**: Claude Sonnet
**Input**: Literal translation + analysis + tone guide
**Output**: Refined poetic translation

**Tone Guide (Rumi's Voice)**:
- **Direct address**: Use "you" and "I" in intimate conversation
- **Ecstatic urgency**: Short exclamations, imperatives ("Come!", "Listen!")
- **Paradox**: Hold contradictions together ("I am silent, yet I speak")
- **Embodied**: Heart, breath, blood, fire, water, wine
- **Contemporary**: Not Victorian, not New Age—clear modern English
- **Intense**: Don't soften, don't explain away

**Anti-patterns to avoid**:
- Academic distance ("one might observe...")
- New Age vagueness ("the universe wants...")
- Over-explanation (trust the image)
- Forced rhyme at expense of meaning

#### Pass 4: QA Agent
**Purpose**: Catch errors before output
**Model**: Claude Sonnet
**Input**: Persian + analysis + final translation
**Output**: QA report with confidence score

**Checks**:
1. **Semantic fidelity**: Does the English mean what the Persian says?
2. **No hallucinations**: Is everything in the translation actually in the original?
3. **Terminology consistency**: Does it match our glossary?
4. **Allusion preservation**: Are Quranic/hadith references intact?
5. **Tone check**: Does it sound like Rumi, not a textbook?
6. **Comparison check**: How does it compare to Arberry/Nicholson (where available)?

**Output**:
```json
{
  "confidence": "high|medium|low",
  "issues": [...],
  "flags_for_human_review": true|false,
  "comparison_notes": "..."
}
```

### 3.3 Batch Consistency Agent (Periodic)

Runs across translated corpus to detect:
- Terminology drift (is "یار" sometimes "Friend" and sometimes "Beloved"?)
- Voice inconsistency (did tone shift?)
- Cross-reference accuracy
- Outlier detection (translations that don't fit the pattern)

---

## 4. Data Pipeline

### 4.1 Source Data

**Primary**: Ganjoor.net API
- Based on Foruzanfar critical edition
- Covers volumes 1-6 of 10 (majority of Divan)
- Structured data with metadata

**Fallback**: Internet Archive scans + OCR

### 4.2 Data Schema

```json
{
  "ghazal": {
    "id": "ganjoor_12345",
    "number": 2114,
    "source": "foruzanfar",
    "meter": "Khafif",
    "rhyme": "-ā",
    "verses": [
      {
        "hemistich1": "ای قوم به حج رفته کجایید کجایید",
        "hemistich2": "معشوق همین جاست بیایید بیایید"
      }
    ]
  },
  "analysis": { ... },
  "translation": {
    "literal": "...",
    "refined": "...",
    "notes": "..."
  },
  "qa": {
    "confidence": "high",
    "flags": [],
    "reviewed": false
  },
  "metadata": {
    "translated_at": "2026-01-22T...",
    "model": "claude-sonnet-4-20250514",
    "pipeline_version": "1.0"
  }
}
```

---

## 5. Phased Execution

### Phase 0: Foundation (Week 1)
**Goal**: Infrastructure and tooling

| Task | Description | Deliverable |
|------|-------------|-------------|
| 0.1 | Finalize terminology glossary | `glossary.json` with 50-100 key terms |
| 0.2 | Create tone reference document | 10 example translations showing target voice |
| 0.3 | Build Ganjoor data fetcher | Working script to pull ghazals |
| 0.4 | Set up output schema | JSON schema + validation |
| 0.5 | Create comparison corpus | 20 ghazals with Arberry/Nicholson translations for benchmarking |

### Phase 1: Proof of Concept (Weeks 2-3)
**Goal**: Validate the multi-agent architecture works

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Implement 4-pass pipeline | Working `translate.py` with all agents |
| 1.2 | Translate pilot corpus (20 ghazals) | `pilot_translations.json` |
| 1.3 | Human review of pilot | Feedback document with corrections |
| 1.4 | Compare to existing translations | Assessment of quality vs. Arberry/Nicholson |
| 1.5 | Iterate on prompts | Refined prompts based on pilot feedback |

**Success criteria**:
- Persian speaker confirms no major errors in 20 ghazals
- Translations preserve Islamic context (Safi test)
- Tone is recognizably "Rumi" (not academic, not New Age)

### Phase 2: First 100 (Weeks 4-6)
**Goal**: Translate a meaningful corpus

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Select 100 ghazals (diverse meters, themes) | `corpus_100.json` |
| 2.2 | Run full pipeline | `translations_100.json` |
| 2.3 | Implement batch consistency check | Consistency report |
| 2.4 | Generate formatted output | HTML, Markdown, PDF |
| 2.5 | Human review (sample) | 20% reviewed by Persian speaker |

**Budget estimate**: ~$50-100 in API costs (4 passes × 100 ghazals × ~$0.15/ghazal)

### Phase 3: Open Source Release (Week 7)
**Goal**: Public launch

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | GitHub repository setup | Public repo with all code |
| 3.2 | Contribution guidelines | CONTRIBUTING.md |
| 3.3 | Documentation | README, methodology doc |
| 3.4 | Sample output publication | Web-viewable translations |
| 3.5 | Outreach | Share with Omid Safi, Rumi scholars |

### Phase 4: Scale (Ongoing)
**Goal**: Translate full Divan with community

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Translate remaining ghazals (3,129 more) | Full corpus |
| 4.2 | Community review system | GitHub issues/PRs for corrections |
| 4.3 | Scholar advisory | Input from Rumi experts |
| 4.4 | Continuous improvement | Re-translate with better models/prompts |

---

## 6. Terminology Glossary (Initial)

| Persian | Transliteration | Translation | Notes |
|---------|-----------------|-------------|-------|
| عشق | 'ishq | Love | Divine love, not mere romance. Capital L when referring to cosmic force. |
| معشوق | ma'shuq | the Beloved | Capital B. Deliberately ambiguous: God, Shams, human beloved. |
| یار | yar | the Friend | Can also be "Beloved" depending on context. |
| دوست | dust | the Friend | Divine friend. |
| جان | jan | soul | Not just "life"—the spiritual essence. |
| دل | del | heart | Seat of spiritual perception, not mere emotion. |
| می | mey | wine | Mystical intoxication, not literal alcohol. |
| مست | mast | intoxicated | Spiritually drunk with divine presence. |
| فنا | fana | annihilation | Of ego in the divine. Keep as "fana" with gloss. |
| بقا | baqa | subsistence | Remaining in God after fana. |
| سماع | sama' | spiritual audition | The whirling ceremony. Keep as "sama'" with gloss. |
| خانقاه | khanaqah | Sufi lodge | Keep as "khanaqah" with gloss. |
| نی | ney | reed-flute | Symbol of soul separated from divine origin. |
| کعبه | Ka'ba | Kaaba | The sacred house in Mecca. Always "Kaaba." |
| نماز | namaz | prayer | The Islamic salat. Keep as "prayer" but note Islamic context. |
| رکوع | ruku' | bowing | Prayer posture. Keep as "ruku'" or "bowing in prayer." |
| سجود | sujud | prostration | Prayer posture. Keep as "sajda" or "prostration in prayer." |
| حج | hajj | Hajj | Pilgrimage to Mecca. Always "Hajj." |
| شمس | Shams | Shams | Shams al-Din Tabrizi. Always proper noun. |

---

## 7. Tone Reference Document

### What Rumi Should Sound Like

**Example 1: Direct Address + Urgency**

> Listen to the reed-flute, how it tells its tale,
> crying out from separations—
>
> "Ever since they cut me from the reed-bed,
> men and women have wept at my cry."

(Not: "The reed-flute narrates its story of separation, which has caused emotional responses in listeners.")

**Example 2: Ecstatic Paradox**

> I am silent, yet I speak.
> I am hidden, yet I shine.
> I am nothing, yet I am everything.

(Not: "The speaker expresses a series of paradoxical statements regarding their ontological status.")

**Example 3: Embodied Spirituality**

> My heart is burning—
> throw no water on this fire!
> Let me burn until nothing remains
> but the Beloved's face.

(Not: "The narrator requests that their spiritual passion not be extinguished, preferring annihilation in divine love.")

**Example 4: Preserved Islamic Context**

> O people who have gone on Hajj—where are you?
> The Beloved is right here! Come, come!
> Your Beloved is your neighbor, wall to wall,
> yet you wander lost in the desert.

(Not: "O spiritual seekers on your journey, the love you seek is already present within you." ← This strips Hajj, Beloved, and the critique of external-only religion.)

---

## 8. Quality Metrics

### 8.1 Automated Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Terminology consistency | % of glossary terms translated consistently | >95% |
| QA confidence | % of translations rated "high" confidence | >70% |
| Allusion preservation | % of Quranic/hadith refs preserved | 100% |
| No hallucinations | % with no added content | 100% |

### 8.2 Human Evaluation (Sample)

| Criterion | Evaluator | Method |
|-----------|-----------|--------|
| Semantic accuracy | Persian speaker | Side-by-side comparison |
| Islamic context preservation | Scholar/Muslim reader | Safi checklist |
| Poetic quality | English reader | Readability + beauty |
| Tone consistency | Multiple readers | Does it sound like Rumi? |

### 8.3 Comparison Benchmarks

For ghazals where Arberry/Nicholson translations exist:
- Our translation should be no less accurate
- Our translation should be more readable
- Our translation should preserve more context than Barks

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM hallucinations | Medium | High | QA agent + human review for low-confidence |
| Terminology drift at scale | Medium | Medium | Batch consistency checker |
| Tone inconsistency | Medium | Medium | Tone reference + few-shot examples |
| Ganjoor API unavailable | Low | High | Cache data locally; fallback to HuggingFace dataset |
| Scholarly criticism | Medium | Medium | Transparent methodology; invite expert review |
| Cost overruns | Low | Low | Start small; monitor costs per ghazal |

---

## 10. Open Questions

1. **Verse numbering**: Should we use Foruzanfar numbers, Ganjoor IDs, or create our own?

2. **Variant readings**: When manuscripts differ, do we translate one reading or note alternatives?

3. **Prose introductions**: Some ghazals have prose context in editions. Translate these too?

4. **Arabic verses**: ~10% of the Divan is in Arabic. Same pipeline or different?

5. **Community contribution model**: GitHub PRs? Dedicated platform? How to handle conflicting suggestions?

6. **Omid Safi involvement**: Should we reach out early for input, or present a finished proof of concept?

---

## 11. Success Criteria

### Minimum Viable Success (Phase 2)
- [ ] 100 ghazals translated with multi-agent pipeline
- [ ] No major semantic errors in human-reviewed sample
- [ ] Islamic context preserved (passes "Safi test")
- [ ] Tone is recognizably Rumi
- [ ] Open source release with documentation

### Full Success (Phase 4)
- [ ] Complete Divan translated (~3,229 ghazals)
- [ ] Community contributions improving translations
- [ ] Positive reception from Rumi scholars
- [ ] Used as reference by students/readers
- [ ] Demonstrates LLM potential for literary translation

---

## 12. Next Steps

Pending your approval of this plan:

1. **Finalize glossary** (task 0.1)
2. **Create tone reference with 10 examples** (task 0.2)
3. **Build the 4-pass pipeline** (task 1.1)
4. **Translate 20 pilot ghazals** (task 1.2)
5. **Review and iterate**

---

## Appendix A: References

- [Omid Safi, *Radical Love* (Yale, 2018)](https://yalebooks.yale.edu/book/9780300248616/radical-love/)
- [Dar-al-Masnavi: Corrections of Popular Versions](https://www.dar-al-masnavi.org/corrections_popular.html)
- [Al Jazeera: A Tale of Two Rumis](https://www.aljazeera.com/features/2023/12/17/a-tale-of-two-rumis-of-the-east-and-of-the-west)
- [Ganjoor.net](https://ganjoor.net) and [Ganjoor API](https://github.com/ganjoor/GanjoorService)
- [Religion News: Omid Safi's 'Radical Love'](https://religionnews.com/2018/06/11/omid-safis-radical-love-recenters-sufi-poetry-within-islam/)
- Arberry, A.J. *Mystical Poems of Rumi* (1968, 1979)
- Nicholson, R.A. *Selected Poems from the Divani Shamsi Tabriz* (1898)

---

*Draft for review. Please provide feedback before we proceed to implementation.*
