"""
Jupyter Notebook translator helper script.

Reads an .ipynb file, extracts markdown cells, writes each cell's content
to a working directory for Claude to translate, then reconstructs the notebook.

This script handles the file I/O and notebook structure manipulation.
The actual translation is performed by Claude or sub-agents.

Usage:
    # Step 1: Prepare cell files
    python translate_notebook.py input.ipynb output.ipynb --lang zh-CN --mode full --workdir ./work

    # Step 2: (Claude translates cell_XXXX.md -> cell_XXXX_translated.md)

    # Step 3: Reconstruct (run again with --reconstruct)
    python translate_notebook.py input.ipynb output.ipynb --lang zh-CN --mode full --workdir ./work --reconstruct

Modes:
    full      - Replace markdown cells with translated content
    bilingual - Insert translated markdown cell below each original
"""

import argparse
import json
import re
import sys
from pathlib import Path


def read_notebook(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_notebook(notebook: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)


def extract_markdown_cells(notebook: dict) -> list[tuple[int, str]]:
    """Return list of (cell_index, markdown_content) for all markdown cells."""
    cells = []
    for idx, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", [])
        if isinstance(source, list):
            content = "".join(source)
        else:
            content = str(source)
        if content.strip():
            cells.append((idx, content))
    return cells


def replace_code_blocks(document: str) -> tuple[str, dict[str, str]]:
    """Replace fenced code blocks with @@CODE_BLOCK_n@@ placeholders."""
    pattern = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~)", re.MULTILINE)
    placeholder_map = {}
    counter = [0]

    def _replace(match):
        key = f"@@CODE_BLOCK_{counter[0]}@@"
        placeholder_map[key] = match.group(0)
        counter[0] += 1
        return key

    result = pattern.sub(_replace, document)
    return result, placeholder_map


def restore_code_blocks(document: str, placeholder_map: dict[str, str]) -> str:
    for key, value in placeholder_map.items():
        document = document.replace(key, value)
    return document


def apply_translation_to_cell(
    cell: dict, translated_content: str, placeholder_map: dict[str, str]
) -> None:
    """Apply translated content back to a cell, restoring code blocks."""
    translated_content = restore_code_blocks(translated_content, placeholder_map)
    source = cell.get("source", [])
    if isinstance(source, list):
        lines = translated_content.splitlines(keepends=True)
        lines = [line if line.endswith("\n") else line + "\n" for line in lines]
        cell["source"] = lines
    else:
        cell["source"] = translated_content


def create_bilingual_cell(translated_content: str, placeholder_map: dict) -> dict:
    """Create a new markdown cell with translated content (for bilingual mode)."""
    translated_content = restore_code_blocks(translated_content, placeholder_map)
    lines = translated_content.splitlines(keepends=True)
    lines = [line if line.endswith("\n") else line + "\n" for line in lines]
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines,
    }


def write_cells_for_translation(cells: list[tuple[int, str]], work_dir: Path) -> None:
    """Write each cell content to a file for translation."""
    for idx, content in cells:
        p = work_dir / f"cell_{idx:04d}.md"
        p.write_text(content, encoding="utf-8")


def read_translated_cells(cells: list[tuple[int, str]], work_dir: Path) -> dict[int, str]:
    """Read translated cell files back; return {cell_index: translated_content}."""
    result = {}
    for idx, _ in cells:
        p = work_dir / f"cell_{idx:04d}_translated.md"
        if p.exists():
            result[idx] = p.read_text(encoding="utf-8").strip()
    return result


def reconstruct_full(
    notebook: dict,
    translations: dict[int, str],
    placeholder_maps: dict[int, dict],
    disclaimer_text: str | None,
) -> dict:
    """Mode A: Replace markdown cells with translated content."""
    for idx, translated in translations.items():
        cell = notebook["cells"][idx]
        apply_translation_to_cell(cell, translated, placeholder_maps.get(idx, {}))

    if disclaimer_text:
        disclaimer_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [disclaimer_text + "\n"],
        }
        notebook["cells"].append(disclaimer_cell)

    return notebook


def reconstruct_bilingual(
    notebook: dict,
    translations: dict[int, str],
    placeholder_maps: dict[int, dict],
    disclaimer_text: str | None,
) -> dict:
    """Mode B: Insert translated markdown cell below each original."""
    offset = 0
    for idx, translated in sorted(translations.items()):
        new_cell = create_bilingual_cell(translated, placeholder_maps.get(idx, {}))
        insert_at = idx + offset + 1
        notebook["cells"].insert(insert_at, new_cell)
        offset += 1

    if disclaimer_text:
        disclaimer_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [disclaimer_text + "\n"],
        }
        notebook["cells"].append(disclaimer_cell)

    return notebook


# ---- Language name lookup ----
LANGUAGE_MAP = {
    "en": "English", "fr": "French", "es": "Spanish", "de": "German",
    "ru": "Russian", "ar": "Arabic", "fa": "Persian (Farsi)", "ur": "Urdu",
    "zh-CN": "Chinese (Simplified)", "zh-TW": "Chinese (Traditional, Taiwan)",
    "zh-HK": "Chinese (Traditional, Hong Kong)", "zh-MO": "Chinese (Traditional, Macau)",
    "ja": "Japanese", "ko": "Korean", "hi": "Hindi", "bn": "Bengali",
    "mr": "Marathi", "ne": "Nepali", "pa": "Punjabi (Gurmukhi)",
    "pt-PT": "Portuguese (Portugal)", "pt-BR": "Portuguese (Brazil)",
    "it": "Italian", "pl": "Polish", "tr": "Turkish", "el": "Greek",
    "th": "Thai", "sv": "Swedish", "da": "Danish", "no": "Norwegian",
    "fi": "Finnish", "nl": "Dutch", "he": "Hebrew", "vi": "Vietnamese",
    "id": "Indonesian", "ms": "Malay", "tl": "Tagalog (Filipino)",
    "sw": "Swahili", "hu": "Hungarian", "cs": "Czech", "sk": "Slovak",
    "ro": "Romanian", "bg": "Bulgarian", "sr": "Serbian (Cyrillic)",
    "hr": "Croatian", "sl": "Slovenian", "my": "Burmese (Myanmar)",
    "uk": "Ukrainian", "lt": "Lithuanian", "ta": "Tamil", "et": "Estonian",
    "te": "Telugu", "ml": "Malayalam", "kn": "Kannada",
    "zh": "Chinese (Simplified)", "pt": "Portuguese",
}

RTL_LANGUAGES = {"ar", "fa", "ur", "he"}


def main():
    parser = argparse.ArgumentParser(description="Translate Jupyter Notebook markdown cells")
    parser.add_argument("input", help="Input .ipynb file path")
    parser.add_argument("output", help="Output .ipynb file path")
    parser.add_argument("--mode", choices=["full", "bilingual"], default="full",
                        help="full=replace cells, bilingual=insert below original")
    parser.add_argument("--lang", required=True, help="Target language code (e.g., zh-CN, ja, ko)")
    parser.add_argument("--no-disclaimer", action="store_true", help="Skip disclaimer cell")
    parser.add_argument("--workdir", required=True, help="Working directory for cell files")
    parser.add_argument("--reconstruct", action="store_true",
                        help="Skip extraction, only reconstruct from existing translated files")
    args = parser.parse_args()

    language_code = args.lang
    language_name = LANGUAGE_MAP.get(language_code, language_code)

    notebook = read_notebook(args.input)
    cells = extract_markdown_cells(notebook)

    if not cells:
        print("No markdown cells found in notebook.")
        write_notebook(notebook, args.output)
        return

    work_dir = Path(args.workdir)
    work_dir.mkdir(parents=True, exist_ok=True)

    if not args.reconstruct:
        # Step 1: Extract and write cell files
        write_cells_for_translation(cells, work_dir)

        # Write info file for sub-agents
        info_file = work_dir / "_info.json"
        info = {
            "language_code": language_code,
            "language_name": language_name,
            "mode": args.mode,
            "cells": [
                {
                    "index": idx,
                    "content_file": f"cell_{idx:04d}.md",
                    "output_file": f"cell_{idx:04d}_translated.md",
                }
                for idx, _ in cells
            ],
        }
        info_file.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"Cell files written to: {work_dir}")
        print(f"Total markdown cells: {len(cells)}")
        print(f"Now translate each cell_XXXX.md -> cell_XXXX_translated.md")
        print(f"Then re-run with --reconstruct to build the output notebook.")
        return

    # Step 2: Reconstruct from translated files
    translations = read_translated_cells(cells, work_dir)

    # Build placeholder maps for each cell (for code block restoration)
    placeholder_maps = {}
    for idx, content in cells:
        _, pmap = replace_code_blocks(content)
        placeholder_maps[idx] = pmap

    if not translations:
        print("No translated files found. Output will be unchanged.")
        write_notebook(notebook, args.output)
        return

    # Check for disclaimer file written by Claude
    disclaimer_text = None
    if not args.no_disclaimer:
        disclaimer_file = work_dir / "_disclaimer.md"
        if disclaimer_file.exists():
            disclaimer_text = disclaimer_file.read_text(encoding="utf-8").strip()
        else:
            # Fallback: generate English disclaimer
            disclaimer_text = (
                "---\n\n"
                "<!-- IPYNB-TRANSLATOR DISCLAIMER: START -->\n"
                f"**Disclaimer**: This document has been machine-translated by "
                f"ipynb-translator (a Claude-based skill). While we strive for accuracy, "
                f"automated translations may contain errors or inaccuracies. "
                f"The original document in its native language should be considered "
                f"the authoritative source.\n"
                "<!-- IPYNB-TRANSLATOR DISCLAIMER: END -->"
            )

    if args.mode == "full":
        notebook = reconstruct_full(notebook, translations, placeholder_maps, disclaimer_text)
    else:
        notebook = reconstruct_bilingual(notebook, translations, placeholder_maps, disclaimer_text)

    write_notebook(notebook, args.output)
    print(f"Translated notebook written to: {args.output}")


if __name__ == "__main__":
    main()
