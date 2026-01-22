#!/usr/bin/env python3
"""
Divan-e Kabir Translation Pipeline
End-to-end system for translating Rumi's poetry using LLMs

Usage:
    python translate.py --input sample_ghazals.json --output translations.json
    python translate.py --api-key YOUR_KEY --model claude-sonnet-4-20250514
"""

import json
import argparse
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

# Import the prompts
from translation_prompt import SYSTEM_PROMPT, format_ghazal_for_translation

@dataclass
class TranslatedGhazal:
    """Structured output for a translated ghazal."""
    number: int
    meter: str
    rhyme: str
    persian_text: list[dict]
    english_translation: str
    scholarly_notes: str
    translator_model: str
    translated_at: str
    confidence: str  # high, medium, low

    def to_dict(self):
        return asdict(self)


def translate_with_anthropic(persian_ghazal: dict, api_key: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Translate a ghazal using the Anthropic API.

    In production, this calls the Claude API. For demo purposes,
    we provide a mock implementation that can be swapped out.
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        user_prompt = format_ghazal_for_translation(persian_ghazal)

        message = client.messages.create(
            model=model,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        return message.content[0].text

    except ImportError:
        print("Warning: anthropic package not installed. Using mock translation.")
        return mock_translate(persian_ghazal)


def mock_translate(ghazal: dict) -> str:
    """
    Mock translation for demonstration when API is unavailable.
    Returns a structured response showing the expected format.
    """
    # This provides realistic example output to demonstrate the pipeline
    mock_translations = {
        2114: """## Translation

**Verse 1:**
O people who have gone on Hajj—where are you, where are you?
The Beloved is right here—come, come!

**Verse 2:**
Your Beloved is your neighbor, wall to wall,
Yet you wander lost in the desert—what air do you seek?

**Verse 3:**
If you behold the formless form of the Beloved,
You become the master, the house, and the Kaaba itself.

---

## Scholarly Notes

**Sufi Context:** This ghazal addresses the tension between external religious practice (Hajj, pilgrimage to Mecca) and internal spiritual realization. Rumi does not dismiss Hajj but critiques those who seek the Divine only in external journeys while ignoring the Beloved's presence within.

**Key Terms:**
- "Hajj" (حج): The Islamic pilgrimage to Mecca, one of the Five Pillars of Islam. Rumi preserves this specifically Islamic reference.
- "The Beloved" (معشوق): Deliberately ambiguous—refers to God, the divine presence, and potentially Shams-i Tabrizi.
- "Kaaba" (کعبه): The sacred house in Mecca. In the final verse, Rumi suggests the realized mystic becomes the Kaaba—the heart becomes the true house of God.

**Quranic Allusion:** The concept of God being closer than one's jugular vein (Quran 50:16) underlies the imagery of the Beloved as "neighbor, wall to wall."

**Lost in Translation:** The Persian "در چه هوایید" (dar che hava'id) contains wordplay—"hava" means both "air/atmosphere" and "desire/whim," suggesting both physical wandering and scattered spiritual aspiration.""",

        1173: """## Translation

**Verse 1:**
Love is the soul of all souls, Love is the affection of all the affectionate,
Love is that which is hidden, Love is that which is manifest—it is He.

**Verse 2:**
From this Love every heart becomes like fire and like water,
Sometimes it burns, sometimes it builds, sometimes it gives, sometimes it takes away—it is He.

**Verse 3:**
In the religion of the lover there is neither disbelief nor faith,
The lover has neither body nor soul—for Love is all soul, it is He.

---

## Scholarly Notes

**Sufi Context:** This ghazal meditates on 'ishq (عشق), divine love, as the animating force of existence. The repeated "او" (u/He) at the end of each couplet points to the divine—a common Sufi rhetorical device.

**Key Terms:**
- "'Ishq" (عشق): Not mere romantic love but the cosmic love that drives creation. In Sufi metaphysics, 'ishq is the force by which God desired to be known and thus created the world.
- "Kufr wa iman" (کفر و ایمان): "Disbelief and faith"—Rumi suggests the lover transcends religious categories, not by abandoning Islam but by reaching a station where such distinctions dissolve in divine unity (tawhid).

**Theological Nuance:** The line "neither disbelief nor faith" should not be read as religious relativism. Rather, it expresses the Sufi teaching that the realized mystic perceives only God—the categories of "believer/disbeliever" apply to the world of forms, not to one annihilated (fana) in divine presence.

**Lost in Translation:** The Persian maintains a hypnotic rhythm through repetition that cannot be fully captured in English.""",

        462: """## Translation

**Verse 1:**
Someone said to me last night: "O friend,
What a light Shams-i Tabrizi is in this world!"

**Verse 2:**
I said to him: "Be silent! Know this moment—
This speech has no end."

**Verse 3:**
Like a moon he shines upon the heavens,
His light is in every heart where the soul resides.

---

## Scholarly Notes

**Historical Context:** This ghazal directly names Shams al-Din Tabrizi (شمس تبریزی), the wandering mystic whose encounter with Rumi transformed the scholar into an ecstatic poet. "Shams" means "sun" in Arabic, and Rumi plays on this throughout—Shams is both the person and the spiritual sun.

**Key Terms:**
- "Shams-i Tabrizi": Rumi's spiritual beloved and teacher. The entire Divan-e Shams is nominally attributed to/dedicated to him.
- The moon/sun imagery creates a paradox: Shams (Sun) shines "like a moon"—suggesting his light is both direct illumination and reflected divine light.

**Sufi Relationship:** The relationship between Rumi and Shams exemplifies the murshid-murid (master-disciple) bond, though Rumi often positions Shams as the greater one. Their relationship scandalized conventional religious authorities of 13th-century Konya.""",

        911: """## Translation

**Verse 1:**
What do I know of what I am intoxicated with? What do I know of what I am?
Heart given, heart given—I have given my heart to the heart-ravisher.

**Verse 2:**
If I had a hundred souls, I would sacrifice them all,
Before that stature, that stature like a tall cypress.

---

## Scholarly Notes

**Sufi Context:** This ghazal exemplifies the "intoxicated" (mast) style of Sufi poetry. The repeated "what do I know" (من چه دانم) expresses the dissolution of rational knowing in mystical experience.

**Key Terms:**
- "Mast" (مست): Spiritually intoxicated—drunk on divine presence, not literal wine. The tavern (meykhaneh) and wine (mey) are standard Sufi symbols for the heart and divine love.
- "Dilbar" (دلبر): "Heart-ravisher"—one who steals hearts. Refers to both human beloved and divine Beloved.
- "Sarv" (سرو): Cypress—a common Persian poetic image for the beloved's tall, graceful stature.

**Ecstatic Dissolution:** The stammering repetition ("heart given, heart given"; "that stature, that stature") mimics the speech of one overwhelmed by spiritual experience—the rational faculties failing in the face of encounter with the divine."""
    }

    if ghazal["number"] in mock_translations:
        return mock_translations[ghazal["number"]]

    # Generic fallback
    return f"""## Translation

[Translation would appear here for Ghazal #{ghazal['number']}]

---

## Scholarly Notes

This is a mock translation for demonstration purposes. In production, this would be generated by the Claude API with the full translation prompt."""


def parse_translation_response(response: str) -> tuple[str, str]:
    """
    Parse the LLM response into translation and notes sections.
    """
    translation = ""
    notes = ""

    # Simple parsing based on expected headers
    if "## Translation" in response and "## Scholarly Notes" in response:
        parts = response.split("## Scholarly Notes")
        translation = parts[0].replace("## Translation", "").strip()
        notes = parts[1].strip() if len(parts) > 1 else ""
    else:
        # Fallback: treat whole response as translation
        translation = response
        notes = ""

    return translation, notes


def translate_ghazal(ghazal: dict, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514") -> TranslatedGhazal:
    """
    Translate a single ghazal and return structured output.
    """
    if api_key:
        raw_response = translate_with_anthropic(ghazal, api_key, model)
    else:
        raw_response = mock_translate(ghazal)

    translation, notes = parse_translation_response(raw_response)

    return TranslatedGhazal(
        number=ghazal["number"],
        meter=ghazal["meter"],
        rhyme=ghazal["rhyme"],
        persian_text=ghazal["verses"],
        english_translation=translation,
        scholarly_notes=notes,
        translator_model=model if api_key else "mock",
        translated_at=datetime.now().isoformat(),
        confidence="medium"  # Would be set by evaluation in production
    )


def translate_collection(input_file: str, output_file: str, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
    """
    Translate all ghazals in a collection file.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    translations = []
    for ghazal in data["ghazals"]:
        print(f"Translating Ghazal #{ghazal['number']}...")
        translated = translate_ghazal(ghazal, api_key, model)
        translations.append(translated.to_dict())

    output = {
        "source": data["source"],
        "edition": data["edition"],
        "translation_method": "LLM (Omid Safi approach)",
        "translated_at": datetime.now().isoformat(),
        "model": model if api_key else "mock",
        "translations": translations
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Translations saved to {output_file}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Translate Rumi's Divan-e Kabir")
    parser.add_argument("--input", "-i", default="sample_ghazals.json", help="Input JSON file with Persian ghazals")
    parser.add_argument("--output", "-o", default="translations.json", help="Output JSON file for translations")
    parser.add_argument("--api-key", help="Anthropic API key (uses mock if not provided)")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Model to use for translation")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    translate_collection(args.input, args.output, api_key, args.model)


if __name__ == "__main__":
    main()
