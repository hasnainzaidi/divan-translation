#!/usr/bin/env python3
"""
Generate formatted output documents from translations.
Supports Markdown and HTML output.
"""

import json
import argparse
from datetime import datetime


def generate_markdown(translations_file: str, output_file: str):
    """Generate a formatted Markdown document."""

    with open(translations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []

    # Header
    lines.append("# Divan-e Kabir: Selected Translations")
    lines.append("")
    lines.append("**From the Poetry of Jalal al-Din Rumi (Mawlana)**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## About This Translation")
    lines.append("")
    lines.append(f"**Source**: {data['source']}")
    lines.append(f"")
    lines.append(f"**Edition**: {data['edition']}")
    lines.append(f"")
    lines.append(f"**Translation Method**: {data['translation_method']}")
    lines.append("")
    lines.append("This translation follows the approach of scholar Omid Safi, preserving the Islamic and Sufi context of Rumi's poetry rather than universalizing it into generic spirituality. Key principles include:")
    lines.append("")
    lines.append("- Preserving references to Islamic prayer, Hajj, Quran, and hadith")
    lines.append("- Maintaining Sufi terminology (fana, baqa, sama', etc.)")
    lines.append("- Keeping the ambiguity of \"the Beloved\" (which may refer to God, Shams, or earthly love)")
    lines.append("- Providing scholarly notes on context and allusions")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Each ghazal
    for t in data["translations"]:
        lines.append(f"## Ghazal {t['number']}")
        lines.append("")
        lines.append(f"*Meter: {t['meter']} | Rhyme: {t['rhyme']}*")
        lines.append("")

        # Persian text
        lines.append("### Persian Text")
        lines.append("")
        for verse in t["persian_text"]:
            lines.append(f"> {verse['hemistich1']}")
            lines.append(f"> {verse['hemistich2']}")
            lines.append(">")
        lines.append("")

        # English translation
        lines.append("### English Translation")
        lines.append("")
        lines.append(t["english_translation"])
        lines.append("")

        # Notes
        if t["scholarly_notes"]:
            lines.append("### Scholarly Notes")
            lines.append("")
            lines.append(t["scholarly_notes"])
            lines.append("")

        lines.append("---")
        lines.append("")

    # Footer
    lines.append("## Colophon")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    lines.append("This is an open-source translation project. Contributions, corrections, and scholarly input are welcome.")
    lines.append("")
    lines.append("*\"The wound is the place where the Light enters you.\" — Rumi*")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Markdown document saved to {output_file}")


def generate_html(translations_file: str, output_file: str):
    """Generate a beautifully formatted HTML document."""

    with open(translations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Divan-e Kabir: Selected Translations</title>
    <style>
        :root {{
            --primary: #1a365d;
            --secondary: #2c5282;
            --accent: #c69749;
            --bg: #faf9f7;
            --text: #2d3748;
            --light: #e2e8f0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Crimson Text', 'Georgia', serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.8;
            padding: 2rem;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            padding: 3rem 0;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 3rem;
        }}

        h1 {{
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
            font-weight: normal;
            letter-spacing: 0.05em;
        }}

        .subtitle {{
            font-size: 1.2rem;
            color: var(--secondary);
            font-style: italic;
        }}

        .about {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 3rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        .about h2 {{
            color: var(--primary);
            font-size: 1.3rem;
            margin-bottom: 1rem;
            font-weight: normal;
        }}

        .about ul {{
            margin-left: 1.5rem;
            margin-top: 1rem;
        }}

        .about li {{
            margin-bottom: 0.5rem;
        }}

        .ghazal {{
            background: white;
            padding: 2.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        .ghazal-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 1px solid var(--light);
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }}

        .ghazal-number {{
            font-size: 1.5rem;
            color: var(--primary);
        }}

        .ghazal-meta {{
            font-size: 0.9rem;
            color: #718096;
            font-style: italic;
        }}

        .persian {{
            direction: rtl;
            text-align: right;
            font-family: 'Noto Naskh Arabic', 'Traditional Arabic', serif;
            font-size: 1.3rem;
            line-height: 2.2;
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
            border-right: 3px solid var(--accent);
        }}

        .persian .verse {{
            margin-bottom: 1rem;
        }}

        .persian .hemistich {{
            display: block;
        }}

        .section-title {{
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--accent);
            margin-bottom: 1rem;
            font-weight: bold;
        }}

        .translation {{
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }}

        .translation p {{
            margin-bottom: 1rem;
        }}

        .translation strong {{
            color: var(--secondary);
        }}

        .notes {{
            background: #f7fafc;
            padding: 1.5rem;
            border-radius: 6px;
            font-size: 0.95rem;
            border-left: 3px solid var(--secondary);
        }}

        .notes p {{
            margin-bottom: 0.8rem;
        }}

        .notes strong {{
            color: var(--primary);
        }}

        .divider {{
            text-align: center;
            padding: 2rem 0;
            color: var(--accent);
            font-size: 1.5rem;
        }}

        footer {{
            text-align: center;
            padding: 3rem 0;
            color: #718096;
            font-style: italic;
            border-top: 2px solid var(--accent);
            margin-top: 2rem;
        }}

        footer .quote {{
            font-size: 1.1rem;
            color: var(--secondary);
            margin-top: 1rem;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 1rem;
            }}

            h1 {{
                font-size: 1.8rem;
            }}

            .ghazal {{
                padding: 1.5rem;
            }}

            .persian {{
                font-size: 1.1rem;
            }}
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Noto+Naskh+Arabic&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>Divan-e Kabir</h1>
            <p class="subtitle">Selected Translations from the Poetry of<br>Jalal al-Din Rumi (Mawlana)</p>
        </header>

        <section class="about">
            <h2>About This Translation</h2>
            <p><strong>Source:</strong> {data['source']}</p>
            <p><strong>Edition:</strong> {data['edition']}</p>
            <p><strong>Method:</strong> {data['translation_method']}</p>
            <p style="margin-top: 1rem;">This translation follows the approach of scholar Omid Safi, preserving the Islamic and Sufi context of Rumi's poetry rather than universalizing it into generic spirituality.</p>
            <ul>
                <li>Preserving references to Islamic prayer, Hajj, Quran, and hadith</li>
                <li>Maintaining Sufi terminology (<em>fana</em>, <em>baqa</em>, <em>sama'</em>, etc.)</li>
                <li>Keeping the ambiguity of "the Beloved"</li>
                <li>Providing scholarly notes on context and allusions</li>
            </ul>
        </section>
"""

    for t in data["translations"]:
        # Format Persian verses
        persian_html = ""
        for verse in t["persian_text"]:
            persian_html += f"""<div class="verse">
                <span class="hemistich">{verse['hemistich1']}</span>
                <span class="hemistich">{verse['hemistich2']}</span>
            </div>"""

        # Format translation (convert markdown-ish to HTML)
        translation_html = t["english_translation"].replace("\n\n", "</p><p>").replace("\n", "<br>")
        if not translation_html.startswith("<p>"):
            translation_html = f"<p>{translation_html}</p>"

        # Format notes
        notes_html = t["scholarly_notes"].replace("\n\n", "</p><p>").replace("\n", "<br>")
        if notes_html and not notes_html.startswith("<p>"):
            notes_html = f"<p>{notes_html}</p>"

        html += f"""
        <article class="ghazal">
            <div class="ghazal-header">
                <span class="ghazal-number">Ghazal {t['number']}</span>
                <span class="ghazal-meta">Meter: {t['meter']} | Rhyme: {t['rhyme']}</span>
            </div>

            <div class="section-title">Persian Text</div>
            <div class="persian">
                {persian_html}
            </div>

            <div class="section-title">English Translation</div>
            <div class="translation">
                {translation_html}
            </div>

            {"<div class='section-title'>Scholarly Notes</div><div class='notes'>" + notes_html + "</div>" if notes_html else ""}
        </article>

        <div class="divider">✦</div>
"""

    html += f"""
        <footer>
            <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            <p>This is an open-source translation project.<br>Contributions, corrections, and scholarly input are welcome.</p>
            <p class="quote">"The wound is the place where the Light enters you." — Rumi</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML document saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate formatted documents from translations")
    parser.add_argument("--input", "-i", default="translations.json", help="Input translations JSON file")
    parser.add_argument("--format", "-f", choices=["markdown", "html", "both"], default="both", help="Output format")
    parser.add_argument("--output", "-o", default="divan_translations", help="Output filename (without extension)")

    args = parser.parse_args()

    if args.format in ["markdown", "both"]:
        generate_markdown(args.input, f"{args.output}.md")

    if args.format in ["html", "both"]:
        generate_html(args.input, f"{args.output}.html")


if __name__ == "__main__":
    main()
