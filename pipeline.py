#!/usr/bin/env python3
"""
Divan-e Kabir Multi-Pass Translation Pipeline

4-pass architecture:
1. Analyzer: Deep understanding of Persian text
2. Translator: Accurate literal translation
3. Stylist: Refine into Rumi's voice
4. QA: Quality assurance check
"""

import json
import os
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
import anthropic

from agents.analyzer import ANALYZER_SYSTEM_PROMPT, get_analyzer_prompt
from agents.translator import TRANSLATOR_SYSTEM_PROMPT, get_translator_prompt
from agents.stylist import STYLIST_SYSTEM_PROMPT, get_stylist_prompt
from agents.qa import QA_SYSTEM_PROMPT, get_qa_prompt


@dataclass
class TranslationResult:
    """Complete translation result from the pipeline."""
    ghazal_id: str
    ghazal_number: int
    persian_text: list
    analysis: dict
    literal_translation: dict
    refined_translation: dict
    qa_result: dict
    final_translation: str
    scholarly_notes: str
    confidence: str
    needs_review: bool
    metadata: dict

    def to_dict(self):
        return asdict(self)


class TranslationPipeline:
    """Multi-pass translation pipeline for Divan-e Kabir."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        self.verbose = True

    def _call_agent(self, system_prompt: str, user_prompt: str, agent_name: str) -> dict:
        """Call an agent and parse JSON response."""
        if self.verbose:
            print(f"  Running {agent_name}...", end=" ", flush=True)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            text = response.content[0].text

            # Try to parse as JSON
            # Sometimes the model wraps in ```json ... ```
            if text.startswith("```"):
                # Extract JSON from code block
                lines = text.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```") and not in_block:
                        in_block = True
                        continue
                    elif line.startswith("```") and in_block:
                        break
                    elif in_block:
                        json_lines.append(line)
                text = "\n".join(json_lines)

            result = json.loads(text)
            if self.verbose:
                print("✓")
            return result

        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"⚠ JSON parse error")
            # Return the raw text wrapped in a dict
            return {"raw_response": text, "parse_error": str(e)}
        except Exception as e:
            if self.verbose:
                print(f"✗ Error: {e}")
            raise

    def translate_ghazal(self, ghazal: dict) -> TranslationResult:
        """
        Run the full 4-pass pipeline on a single ghazal.
        """
        ghazal_num = ghazal.get("number", "?")
        print(f"\n{'='*60}")
        print(f"Translating Ghazal #{ghazal_num}")
        print(f"{'='*60}")

        # Pass 1: Analysis
        analysis = self._call_agent(
            ANALYZER_SYSTEM_PROMPT,
            get_analyzer_prompt(ghazal),
            "Analyzer"
        )

        # Pass 2: Literal Translation
        literal = self._call_agent(
            TRANSLATOR_SYSTEM_PROMPT,
            get_translator_prompt(ghazal, analysis),
            "Translator"
        )

        # Pass 3: Stylistic Refinement
        literal_for_stylist = literal.get("literal_translation", literal)
        refined = self._call_agent(
            STYLIST_SYSTEM_PROMPT,
            get_stylist_prompt(ghazal, analysis, literal_for_stylist),
            "Stylist"
        )

        # Pass 4: QA Check
        refined_for_qa = refined.get("refined_translation", refined)
        qa = self._call_agent(
            QA_SYSTEM_PROMPT,
            get_qa_prompt(ghazal, analysis, literal_for_stylist, refined_for_qa),
            "QA"
        )

        # Extract final translation
        final_text = self._extract_final_translation(refined)
        notes = self._compile_scholarly_notes(analysis, literal)

        # Determine confidence and review flag
        confidence = qa.get("confidence", "medium")
        needs_review = qa.get("flags_for_human_review", confidence == "low")

        result = TranslationResult(
            ghazal_id=f"F-{ghazal_num}",
            ghazal_number=ghazal_num,
            persian_text=ghazal["verses"],
            analysis=analysis,
            literal_translation=literal,
            refined_translation=refined,
            qa_result=qa,
            final_translation=final_text,
            scholarly_notes=notes,
            confidence=confidence,
            needs_review=needs_review,
            metadata={
                "translated_at": datetime.now().isoformat(),
                "model": self.model,
                "pipeline_version": "1.1"
            }
        )

        # Print summary
        self._print_summary(result)

        return result

    def _extract_final_translation(self, refined: dict) -> str:
        """Extract the final translation text from refined output."""
        if "refined_translation" in refined:
            rt = refined["refined_translation"]
            if "full_text" in rt:
                return rt["full_text"]
            elif "verses" in rt:
                lines = []
                for v in rt["verses"]:
                    lines.append(v.get("line1", ""))
                    lines.append(v.get("line2", ""))
                return "\n".join(lines)
        return str(refined)

    def _compile_scholarly_notes(self, analysis: dict, literal: dict) -> str:
        """Compile scholarly notes from analysis."""
        notes = []

        # Quranic allusions
        if analysis.get("quranic_allusions"):
            notes.append("**Quranic Allusions:**")
            for a in analysis["quranic_allusions"]:
                notes.append(f"- {a.get('reference', '?')}: {a.get('meaning', a.get('rumi_usage', ''))}")

        # Sufi terminology
        if analysis.get("sufi_terminology"):
            notes.append("\n**Sufi Terminology:**")
            for t in analysis["sufi_terminology"]:
                notes.append(f"- *{t.get('term', '')}* ({t.get('persian', '')}): {t.get('meaning_in_context', '')}")

        # Ambiguities
        if analysis.get("ambiguities"):
            notes.append("\n**Deliberate Ambiguities:**")
            for a in analysis["ambiguities"]:
                readings = ", ".join(a.get("possible_readings", []))
                notes.append(f"- \"{a.get('phrase', '')}\": {readings}")

        # Wordplay
        if analysis.get("wordplay"):
            notes.append("\n**Wordplay (Lost in Translation):**")
            for w in analysis["wordplay"]:
                meanings = ", ".join(w.get("meanings", []))
                notes.append(f"- *{w.get('word', '')}*: {meanings}")

        # Translation notes
        if literal.get("translation_notes"):
            notes.append("\n**Translation Notes:**")
            for n in literal["translation_notes"]:
                notes.append(f"- Verse {n.get('verse', '?')}: {n.get('note', '')}")

        return "\n".join(notes) if notes else ""

    def _print_summary(self, result: TranslationResult):
        """Print a summary of the translation."""
        print(f"\n--- Translation Result ---")
        print(f"Confidence: {result.confidence.upper()}")
        if result.needs_review:
            print(f"⚠️  FLAGGED FOR HUMAN REVIEW")

        print(f"\n--- Final Translation ---")
        print(result.final_translation)

        if result.qa_result.get("overall_issues"):
            print(f"\n--- QA Issues ---")
            for issue in result.qa_result["overall_issues"]:
                print(f"  - {issue}")


def translate_corpus(input_file: str, output_file: str, limit: Optional[int] = None):
    """Translate a corpus of ghazals."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pipeline = TranslationPipeline()

    results = []
    ghazals = data["ghazals"][:limit] if limit else data["ghazals"]

    for ghazal in ghazals:
        try:
            result = pipeline.translate_ghazal(ghazal)
            results.append(result.to_dict())
        except Exception as e:
            print(f"Error translating ghazal {ghazal.get('number', '?')}: {e}")
            continue

    output = {
        "source": data.get("source", "Divan-e Kabir"),
        "edition": data.get("edition", "Unknown"),
        "translation_method": "Multi-pass LLM (Analyzer → Translator → Stylist → QA)",
        "translated_at": datetime.now().isoformat(),
        "pipeline_version": "1.1",
        "translations": results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Saved {len(results)} translations to {output_file}")

    # Summary stats
    high = sum(1 for r in results if r["confidence"] == "high")
    medium = sum(1 for r in results if r["confidence"] == "medium")
    low = sum(1 for r in results if r["confidence"] == "low")
    review = sum(1 for r in results if r["needs_review"])

    print(f"Confidence: {high} high, {medium} medium, {low} low")
    print(f"Flagged for review: {review}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Translate Divan-e Kabir ghazals")
    parser.add_argument("--input", "-i", default="sample_ghazals.json")
    parser.add_argument("--output", "-o", default="pipeline_translations.json")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of ghazals")
    parser.add_argument("--api-key", "-k", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")

    args = parser.parse_args()

    # Set API key from argument if provided
    if args.api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.api_key

    # Check if key is available
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set or is empty.")
        print("Please either:")
        print("  1. Set the environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("  2. Pass it as an argument: python pipeline.py --api-key 'your-key'")
        sys.exit(1)

    translate_corpus(args.input, args.output, args.limit)
