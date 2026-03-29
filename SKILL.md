---
name: ipynb-translator
description: Translate Jupyter Notebook (.ipynb) files to target languages using Claude itself as the translation engine. Use when the user wants to (1) translate a .ipynb file to another language, (2) create bilingual notebooks with translated cells below originals, (3) batch-translate notebooks for multiple languages. Triggers on mentions of notebook translation, ipynb translation, or translating Jupyter notebooks.
---

# IPYNB Translator

Translate Jupyter Notebook files by leveraging Claude directly (no external LLM API needed).

## Workflow

1. **Parse** - Read the .ipynb JSON, extract markdown cells (skip code cells entirely)
2. **Prepare** - Replace fenced code blocks with `@@CODE_BLOCK_n@@` placeholders
3. **Translate** - Translate each cell following the rules in [references/translation-rules.md](references/translation-rules.md)
4. **Restore** - Put code blocks back, normalize CJK emphasis if applicable
5. **Reconstruct** - Build the output notebook in the chosen mode

## Output Modes

### Mode A: `full`
Replace each markdown cell with its translation. Add optional disclaimer cell at the end.

### Mode B: `bilingual`
Keep original markdown cells intact. Insert a new translated markdown cell immediately below each original. Add optional disclaimer cell at the end. Useful for side-by-side comparison.

## Translation Rules

All detailed rules — prompts, code block handling, CJK normalization, disclaimer templates — are in [references/translation-rules.md](references/translation-rules.md). Read that file before starting any translation.

## Step-by-Step Procedure

1. Run `scripts/translate_notebook.py` to extract markdown cells into a working directory:
   ```bash
   python scripts/translate_notebook.py input.ipynb output.ipynb --lang zh-CN --mode full --workdir ./work
   ```
   This creates `cell_0000.md`, `cell_0001.md`, etc. in `./work/`, along with `_info.json`.

2. Read `_info.json` to get the cell list, then translate each `cell_XXXX.md` → `cell_XXXX_translated.md` using sub-agents (Agent tool). Max 2 concurrent sub-agents. Each sub-agent must include the translation rules from [references/translation-rules.md](references/translation-rules.md) in its prompt.

3. Generate disclaimer in the target language and write to `./work/_disclaimer.md`.

4. Reconstruct the notebook:
   ```bash
   python scripts/translate_notebook.py input.ipynb output.ipynb --lang zh-CN --mode full --workdir ./work --reconstruct
   ```

### For multi-language batch translation:

1. For each target language, repeat steps 1–4 above with different `--lang` and `--workdir`
2. Write outputs to separate files: `notebook.zh-CN.ipynb`, `notebook.ja.ipynb`, etc.

## Supported Languages

See [references/languages.md](references/languages.md) for the full mapping (56 languages).

Common codes: `zh-CN`, `zh-TW`, `ja`, `ko`, `fr`, `es`, `de`, `pt-BR`, `ru`, `ar`, `hi`.
