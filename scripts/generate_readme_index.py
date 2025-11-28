#!/usr/bin/env python3
import os

# Map ISO code to native endonym
ENDONYMS = {
    "ar": "العربية",
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "ko": "한국어",
    "ja": "日本語",
    "pt": "Português",
    "ru": "Русский",
    "zh-Hant": "中文（繁體）",
    "zh-Hans": "中文（简体）",
}

def find_language_readmes():
    files = os.listdir(".")
    readmes = []
    for f in files:
        if f.startswith("README.") and f.endswith(".md") and f != "README.md":
            code = f[7:-3]  # extract XX from README.XX.md
            if code in ENDONYMS:
                readmes.append((ENDONYMS[code], code, f))
    return readmes

def generate_readme_index(readmes):
    readmes_sorted = sorted(readmes, key=lambda x: x[0])

    lines = ["# 🌍", ""]
    for native, code, filename in readmes_sorted:
        lines.append(f"- [{native}]({filename})")
    lines.append("")

    return "\n".join(lines)

def main():
    readmes = find_language_readmes()
    output = generate_readme_index(readmes)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)
    print("README.md generated successfully.")

if __name__ == "__main__":
    main()
