# Translation Rules

## Code Comment Translation

When code blocks contain comments, translate only the comment text while preserving code structure:

### Comment Style Detection

| Language Hint | Comment Style | Languages |
|---|---|---|
| python, py, bash, sh, shell, ps1, powershell, r, ruby, rb | `#` | Hash-style |
| javascript, js, typescript, ts, java, c, cpp, c++, c#, cs, go, rust, swift, kotlin, scala, php | `//` | Slash-style |

### Batch Comment Translation Prompt

```
Translate the following code comments to {language_name} ({language_code}).
Each line is in the form 'COMMENT_n: <text>'.
Translate only the text after the colon into the target language.
Keep the 'COMMENT_n:' prefix exactly the same and in English.
Return the same number of lines, with the same COMMENT_n numbers, one per line.
Do not add, remove, or reorder lines.
Do not add any explanations or extra text.
```

### Mermaid Diagram Translation

For ```mermaid code blocks, use this prompt:

```
Translate the following Mermaid diagram code to {language_name} ({language_code}).
Preserve all Mermaid syntax and structure exactly, including keywords (graph, subgraph, end),
node IDs, arrows, style/class definitions, and URLs.
Only translate human-readable text, such as labels in square brackets [Like this], text inside quotes "Like this",
and comment text after %% markers.
Do not change node IDs, arrow syntax, style declarations, or URLs/paths.
Return only the translated Mermaid code block without any explanations or extra text.
```

## CJK Emphasis Normalization

For target languages `ja`, `ko`, `zh-*`: after translation, convert `*emphasis*` adjacent to CJK characters to HTML tags.

### Pattern

CJK character class: `\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af`

When emphasis markers (`*`, `**`, `***`) are directly adjacent to CJK characters on either side, convert:
- `*text*` → `<em>text</em>`
- `**text**` → `<strong>text</strong>`
- `***text***` → `<strong><em>text</em></strong>`

### Skip rules
- Do NOT normalize inside inline code spans (`` ` ``)
- Only apply when the delimiter is directly adjacent to a CJK character

## Language-Specific Prompt Additions

### Japanese (ja)
Append to the translation prompt:
```
Japanese mode: preserve Markdown tokens strictly.
Rules (must follow):
1) Keep Markdown links exactly: [text](URL) -> [translated text](same URL).
2) NEVER rewrite links as plain text (e.g., 「text」（URL）, text (URL)).
3) Translate only link text; keep Markdown structure and URL unchanged.
4) Do not add 「」 around a Markdown link unless outside-link grammar requires it.
STRUCTURE IS MORE IMPORTANT THAN STYLE.
```

## RTL Language Handling

RTL languages: `ar`, `fa`, `ur`, `he`

For these languages, append to the translation prompt:
```
Please write the output from right to left, respecting that this is a right-to-left language.
```

## Disclaimer Templates by Language

The disclaimer cell must be generated in the target language. Below are templates for common languages. For languages not listed, translate the English template.

### English (en)
```
**Disclaimer**: This document has been machine-translated by ipynb-translator (an AI-powered translation tool). While we strive for accuracy, automated translations may contain errors or inaccuracies. The original document in its native language should be considered the authoritative source.
```

### Chinese Simplified (zh-CN)
```
**免责声明**：本文档由 ipynb-translator（基于 AI 的翻译工具）进行机器翻译。虽然我们力求准确，但自动翻译可能存在错误或不准确之处。原始语言的文档应被视为权威来源。
```

### Japanese (ja)
```
**免責事項**：このドキュメントは ipynb-translator（AI ベースの翻訳ツール）によって機械翻訳されています。正確性を追求していますが、自動翻訳には誤りや不正確な部分が含まれる可能性があります。元の言語での原文を権威ある情報源としてご参照ください。
```

### Korean (ko)
```
**면책 조항**: 이 문서는 ipynb-translator(AI 기반 번역 도구)에 의해 기계 번역되었습니다. 정확성을 위해 노력하고 있지만, 자동 번역에는 오류나 부정확한 부분이 있을 수 있습니다. 원본 언어로 된 원문을 권위 있는 출처로 간주해 주십시오.
```

### French (fr)
```
**Avertissement** : Ce document a été traduit automatiquement par ipynb-translator (un outil de traduction basé sur l'IA). Bien que nous nous efforcions d'assurer l'exactitude, les traductions automatiques peuvent contenir des erreurs ou des inexactitudes. Le document original dans sa langue d'origine doit être considéré comme la source faisant autorité.
```

### Spanish (es)
```
**Aviso legal**: Este documento ha sido traducido automáticamente por ipynb-translator (una herramienta de tradacción basada en IA). Aunque nos esforzamos por lograr la precisión, las traducciones automatizadas pueden contener errores o inexactitudes. El documento original en su idioma nativo debe considerarse la fuente autorizada.
```

### German (de)
```
**Haftungsausschluss**: Dieses Dokument wurde von ipynb-translator (einem KI-basierten Übersetzungswerkzeug) maschinell übersetzt. Obwohl wir uns um Genauigkeit bemühen, können automatische Übersetzungen Fehler oder Ungenauigkeiten enthalten. Das Originaldokument in seiner Ursprungssprache gilt als maßgebliche Quelle.
```

### Portuguese Brazil (pt-BR)
```
**Aviso**: Este documento foi traduzido automaticamente pelo ipynb-translator (uma ferramenta de tradução baseada em IA). Embora nos esforcemos pela precisão, traduções automáticas podem conter erros ou imprecisões. O documento original em seu idioma nativo deve ser considerado a fonte autorizada.
```

### Russian (ru)
```
**Отказ от ответственности**: Этот документ переведён автоматически с помощью ipynb-translator (инструмента перевода на основе ИИ). Хотя мы стремимся к точности, автоматические переводы могут содержать ошибки или неточности. Оригинальный документ на исходном языке следует считать авторитетным источником.
```

### Arabic (ar)
```
**إخلاء مسؤولية**: تمت ترجمة هذا المستند آليًا بواسطة ipynb-translator (أداة ترجمة مبنية على الذكاء الاصطناعي). بينما نسعى لتحقيق الدقة، قد تحتوي الترجمات الآلية على أخطاء أو عدم دقة. يجب اعتبار المستند الأصلي بلغته الأصلية هو المصدر الموثوق.
```

### Hindi (hi)
```
**अस्वीकरण**: यह दस्तावेज़ ipynb-translator (AI-आधारित अनुवाद उपकरण) द्वारा मशीनी अनुवादित किया गया है। हम सटीकता का प्रयास करते हैं, फिर भी स्वचालित अनुवादों में त्रुटियाँ हो सकती हैं। मूल भाषा में मूल दस्तावेज़ को प्रामाणिक स्रोत माना जाना चाहिए।
```
