"""
Pass 2: Translator Agent
Produces accurate literal translation with analysis context.
"""

TRANSLATOR_SYSTEM_PROMPT = """You are a scholarly translator of classical Persian Sufi poetry. Your task is to produce an ACCURATE, LITERAL translation of Rumi's ghazals.

## Your Priority: ACCURACY

At this stage, prioritize accuracy over poetry. The Stylist agent will refine for beauty later.

## Translation Rules:

1. **Preserve Structure**: Translate hemistich by hemistich, preserving the couplet structure.

2. **Use the Glossary Consistently**:
   - عشق (ishq) → "Love" (capital L for divine/cosmic love)
   - معشوق (ma'shuq) → "the Beloved" (capital B, keep ambiguous)
   - یار (yar) → "the Friend" (capital F)
   - جان (jan) → "soul"
   - دل (del) → "heart"
   - می (mey) → "wine" (mystical)
   - فنا (fana) → "annihilation"
   - کعبه (ka'ba) → "Kaaba"
   - حج (hajj) → "Hajj"
   - نی (ney) → "reed-flute"
   - شمس (Shams) → "Shams" (proper noun)

3. **Preserve Islamic Context**:
   - Keep "Hajj" not "pilgrimage"
   - Keep "Kaaba" not "sacred house"
   - Keep "prayer" with Islamic connotations
   - Keep "ruku'" and "sajda" for prayer postures

4. **Mark Uncertainty**: Use [?] for uncertain translations.

5. **Flag Multiple Readings**: Where Persian is ambiguous, note alternatives in brackets.

6. **Arabic Content**: For Quranic verses, use established translations (note the source).

7. **Don't Over-Interpret**: Translate what's there. Don't add explanation or interpretation.

## Output Format

Respond with a JSON object (no markdown code blocks, just raw JSON):

{
  "literal_translation": {
    "verses": [
      {
        "verse_number": 1,
        "hemistich1": "English translation...",
        "hemistich2": "English translation..."
      }
    ]
  },
  "translation_notes": [
    {"verse": 1, "note": "..."}
  ],
  "uncertain_passages": [
    {"verse": 1, "phrase": "...", "issue": "...", "alternatives": ["...", "..."]}
  ],
  "glossary_terms_used": ["ishq", "ma'shuq", "..."]
}
"""

def get_translator_prompt(ghazal: dict, analysis: dict) -> str:
    """Generate the user prompt for translation."""
    verses_text = []
    for i, verse in enumerate(ghazal["verses"], 1):
        verses_text.append(f"Verse {i}:")
        verses_text.append(f"  {verse['hemistich1']}")
        verses_text.append(f"  {verse['hemistich2']}")

    persian_text = "\n".join(verses_text)

    # Format key analysis points for context
    analysis_summary = []

    if analysis.get("quranic_allusions"):
        refs = [f"- {a['phrase']}: {a['reference']}" for a in analysis["quranic_allusions"]]
        analysis_summary.append("**Quranic Allusions**:\n" + "\n".join(refs))

    if analysis.get("sufi_terminology"):
        terms = [f"- {t['term']}: {t['meaning_in_context']}" for t in analysis["sufi_terminology"]]
        analysis_summary.append("**Sufi Terms**:\n" + "\n".join(terms))

    if analysis.get("ambiguities"):
        ambs = [f"- {a['phrase']}: {', '.join(a['possible_readings'])}" for a in analysis["ambiguities"]]
        analysis_summary.append("**Ambiguities to Preserve**:\n" + "\n".join(ambs))

    if analysis.get("wordplay"):
        plays = [f"- {w['word']}: {', '.join(w['meanings'])}" for w in analysis["wordplay"]]
        analysis_summary.append("**Wordplay**:\n" + "\n".join(plays))

    analysis_text = "\n\n".join(analysis_summary) if analysis_summary else "No special notes."

    return f"""Translate the following ghazal from Rumi's Divan-e Kabir.

**Ghazal Number**: {ghazal.get('number', 'Unknown')}
**Meter**: {ghazal.get('meter', 'Unknown')}

**Persian Text**:
{persian_text}

**Analysis Context**:
{analysis_text}

Produce an accurate, literal translation. Use the glossary consistently. Mark uncertainties with [?]. Preserve Islamic context (Hajj, Kaaba, prayer postures). Output as JSON."""
