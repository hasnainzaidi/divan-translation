# Divan-e Kabir Translation Project

An open-source project to translate Rumi's complete Divan-e Shams (Divan-e Kabir) from Persian to English using large language models, following the scholarly approach of Omid Safi.

## Philosophy

This project aims to create translations that:

1. **Preserve Islamic and Sufi context** — Unlike many popular Rumi translations that strip away religious context, we keep references to Islamic prayer, Hajj, Quranic allusions, and Sufi terminology intact.

2. **Maintain scholarly accuracy** — Translations prioritize meaning over forced rhyme, with annotations explaining lost wordplay and cultural context.

3. **Honor ambiguity** — Persian mystical poetry is deliberately multilayered. We don't collapse "the Beloved" (ma'shuq) into a single interpretation.

4. **Enable community improvement** — All translations are open for correction and refinement.

## Quick Start

### 1. Generate Sample Translations (Demo Mode)

```bash
# Uses mock translations to demonstrate the pipeline
cd divan-translation
python translate.py --input sample_ghazals.json --output translations.json
python generate_document.py --input translations.json --format both
```

This produces `divan_translations.md` and `divan_translations.html`.

### 2. Generate Real Translations (With API Key)

```bash
export ANTHROPIC_API_KEY=your_key_here
python translate.py --input sample_ghazals.json --output translations.json
```

### 3. Fetch Source Data from Ganjoor

```bash
# Fetch 100 ghazals from Rumi's Divan
python ganjoor_fetcher.py --limit 100 --output ganjoor_ghazals.json

# Then translate them
python translate.py --input ganjoor_ghazals.json --output full_translations.json
```

## Project Structure

```
divan-translation/
├── README.md                 # This file
├── sample_ghazals.json       # Sample Persian source texts
├── translation_prompt.py     # LLM prompt design (Omid Safi approach)
├── translate.py              # Main translation pipeline
├── ganjoor_fetcher.py        # Fetch Persian texts from Ganjoor API
├── generate_document.py      # Generate formatted output (MD, HTML)
├── translations.json         # Translation output (JSON)
├── divan_translations.md     # Formatted Markdown output
└── divan_translations.html   # Formatted HTML output
```

## The Translation Prompt

The system prompt in `translation_prompt.py` instructs the LLM to:

- Preserve Sufi terminology (fana, baqa, sama', etc.)
- Keep Quranic/hadith references
- Maintain the verse structure (beyt/couplet)
- Provide scholarly annotations
- Avoid "New Age" universalization

Key terminology is handled consistently:
- عشق (eshq) → "Love" (divine love)
- معشوق (ma'shuq) → "the Beloved" (capital B, ambiguous)
- جان (jan) → "soul" (not just "life")
- می (mey) → "wine" (mystical intoxication)

## Data Sources

### Ganjoor.net
- Largest Persian poetry database
- Free API: https://api.ganjoor.net
- Based on Foruzanfar's critical edition
- ~40,000 verses of Divan-e Shams

### Alternative Sources
- Internet Archive: Scanned editions
- Hugging Face: `kakooch/ganjoor-processed` dataset

## Contributing

This is a community project. Ways to contribute:

1. **Translation Review** — Persian speakers can review and correct translations
2. **Scholarly Notes** — Add context, references, and explanations
3. **Code Improvements** — Enhance the pipeline, add new output formats
4. **Documentation** — Improve guides and glossaries

## Roadmap

- [x] End-to-end pipeline demonstration
- [x] Omid Safi-style translation prompt
- [x] Ganjoor API integration
- [ ] Translate first 100 ghazals with human review
- [ ] Build terminology consistency checker
- [ ] Add TEI-XML output for scholars
- [ ] Create contribution guidelines
- [ ] Scholar review process

## References

- **Omid Safi** — [Duke University](https://scholars.duke.edu/person/omid.safi), author of works on Rumi
- **Ganjoor** — [ganjoor.net](https://ganjoor.net), [GitHub](https://github.com/ganjoor)
- **Foruzanfar Edition** — Badi' al-Zaman Foruzanfar's critical 10-volume edition (1957-1967)
- **Dar-al-Masnavi** — [dar-al-masnavi.org](https://dar-al-masnavi.org), scholarly Rumi resources

## License

Open source. Translations are released for community use and improvement.

---

*"The wound is the place where the Light enters you." — Rumi*
