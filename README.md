# ipynb-translator
A skill for translating Jupyter Notebook (`.ipynb`) files using an LLM as the translation engine.

## Features
- Translate markdown cells in `.ipynb` files
- Bilingual mode: keep original + insert translated cells
- Batch translation for multiple languages
- Preserve code blocks and notebook structure
- Support 50+ languages including zh-CN, ja, ko, fr, es, etc.

## Usage
This skill parses Jupyter notebooks, extracts markdown content, translates text via LLM, and reconstructs a complete notebook in either full-translation or bilingual side-by-side mode.
