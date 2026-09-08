#!/usr/bin/env python3
"""summary-ko 폴더의 마크다운 정리본을 하나의 PDF로 묶는다."""

import re
from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "summary-ko"
OUT = ROOT / "세계는-어떻게-모든-것이-동나게-되었나-한국어-정리본.pdf"

BOOK_TITLE = "세계는 어떻게 모든 것이 동나게 되었나"
BOOK_SUB = "글로벌 공급망의 안쪽"
BOOK_ORIG = "Peter S. Goodman, <i>How the World Ran Out of Everything: Inside the Global Supply Chain</i> (Mariner Books, 2024)"

CSS = """
@page {
  size: A4;
  margin: 24mm 22mm 20mm 22mm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #8a8a8a; }
}
@page cover { margin: 0; @bottom-center { content: none; } }
@page toc  { @bottom-center { content: none; } }

html { font-family: "Noto Serif CJK KR", serif; font-size: 10.5pt; line-height: 1.75; color: #1c1c1c; }
body { margin: 0; }

section.cover { page: cover; height: 297mm; display: flex; flex-direction: column;
  justify-content: center; padding: 0 30mm; background: #f7f5f1; break-after: page; }
section.cover .kicker { font-family: "Noto Sans CJK KR", sans-serif; font-size: 10pt;
  letter-spacing: .28em; color: #8a7f6d; margin-bottom: 14mm; }
section.cover h1 { font-family: "Noto Sans CJK KR", sans-serif; font-size: 30pt; font-weight: 700;
  line-height: 1.35; margin: 0 0 6mm; color: #141414; }
section.cover .sub { font-size: 14pt; color: #4a4a4a; margin-bottom: 22mm; }
section.cover .orig { font-size: 9.5pt; color: #6b6b6b; line-height: 1.9; border-top: 1px solid #d8d2c7; padding-top: 8mm; }

section.toc { page: toc; break-after: page; }
section.toc h2 { font-family: "Noto Sans CJK KR", sans-serif; font-size: 16pt; margin: 0 0 10mm;
  padding-bottom: 4mm; border-bottom: 1px solid #ddd; }
section.toc .part { font-family: "Noto Sans CJK KR", sans-serif; font-size: 10pt; color: #8a7f6d;
  letter-spacing: .12em; margin: 8mm 0 3mm; }
section.toc ol { list-style: none; margin: 0; padding: 0; }
section.toc li { margin: 0 0 2.6mm; font-size: 10pt; }
section.toc a { text-decoration: none; color: #1c1c1c; }
section.toc a::after { content: " " leader('.') " " target-counter(attr(href), page); color: #999; }

section.doc { break-before: page; }
h1 { font-family: "Noto Sans CJK KR", sans-serif; font-size: 20pt; font-weight: 700;
  line-height: 1.4; margin: 0 0 3mm; color: #111; }
p.subtitle { font-family: "Noto Sans CJK KR", sans-serif; font-size: 10.5pt; color: #8a7f6d;
  margin: 0 0 7mm; padding-bottom: 5mm; border-bottom: 2px solid #e6e1d8; }
h2 { font-family: "Noto Sans CJK KR", sans-serif; font-size: 13pt; font-weight: 700;
  margin: 9mm 0 3.5mm; color: #1a1a1a; break-after: avoid; }
p { margin: 0 0 3.6mm; text-align: justify; }
strong { font-weight: 700; }

blockquote { margin: 0 0 7mm; padding: 4.5mm 6mm; background: #f6f4ef; border-left: 3px solid #c9bfa9; }
blockquote p { margin: 0 0 2mm; font-size: 10pt; }
blockquote p:last-child { margin-bottom: 0; }

hr { border: 0; border-top: 1px solid #e8e4dc; margin: 7mm 0; }

table { width: 100%; border-collapse: collapse; margin: 4mm 0 6mm; font-size: 9.2pt;
  break-inside: avoid; }
th { background: #f2efe9; font-family: "Noto Sans CJK KR", sans-serif; font-weight: 700;
  text-align: left; padding: 2.2mm 3mm; border-bottom: 1.5px solid #cfc7b6; }
td { padding: 2.2mm 3mm; border-bottom: 1px solid #e8e4dc; vertical-align: top; }

ul, ol { margin: 0 0 4mm; padding-left: 6mm; }
li { margin-bottom: 1.6mm; }

.footnote { font-size: 9pt; color: #555; border-top: 1px solid #e0e0e0; margin-top: 8mm; padding-top: 3mm; }
.footnote ol { padding-left: 5mm; }
sup a { text-decoration: none; color: #8a7f6d; }

section.colophon { break-before: page; font-size: 9.5pt; color: #555; }
section.colophon h2 { font-size: 13pt; color: #1a1a1a; }
"""

# 원서의 3부 구성에 맞춰 목차를 나눈다.
PARTS = {
    "01": "1부. 대공급망 붕괴",
    "08": "2부. 바다를 건너",
    "18": "3부. 세계화가 집으로 돌아오다",
}


def convert(path: Path, anchor: str) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.split("\n")

    title = lines[0].lstrip("# ").strip()
    body_lines = lines[1:]

    subtitle = ""
    for i, line in enumerate(body_lines):
        if line.startswith("부제: "):
            subtitle = line[len("부제: "):].strip()
            body_lines[i] = ""
            break

    html = markdown.markdown(
        "\n".join(body_lines),
        extensions=["tables", "footnotes", "sane_lists"],
        extension_configs={"footnotes": {"BACKLINK_TEXT": ""}},
    )
    # 첫 인용문(한 줄 요약)에서 라벨 줄을 없애 문장만 남긴다.
    html = html.replace("<strong>한 줄 요약</strong><br />\n", "", 1)

    head = f'<h1 id="{anchor}">{title}</h1>'
    if subtitle:
        head += f'<p class="subtitle">{subtitle}</p>'
    return title, f'<section class="doc">{head}{html}</section>'


def main() -> None:
    files = sorted(p for p in SRC.glob("*.md") if p.name != "README.md")
    docs, toc_rows = [], []

    for path in files:
        num = path.name[:2]
        anchor = f"doc-{num}"
        title, html = convert(path, anchor)
        if num in PARTS:
            toc_rows.append(f'<div class="part">{PARTS[num]}</div>')
        toc_rows.append(f'<li><a href="#{anchor}">{title}</a></li>')
        docs.append(html)

    toc = "".join(toc_rows)
    toc = re.sub(r"(<li>.*?</li>)(?=<div|$)", r"<ol>\1</ol>", toc, flags=re.S)
    toc = toc.replace("</li><li>", "</li><li>")

    page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>{BOOK_TITLE}</title><style>{CSS}</style></head><body>
<section class="cover">
  <div class="kicker">한국어 정리본</div>
  <h1>{BOOK_TITLE}</h1>
  <div class="sub">{BOOK_SUB}</div>
  <div class="orig">{BOOK_ORIG}<br>원서를 읽고 논지와 사실 관계를 한국어로 재구성한 요약본이다.</div>
</section>
<section class="toc"><h2>차례</h2>{toc}</section>
{''.join(docs)}
<section class="colophon"><h2>이 문서에 관하여</h2>
<p>이 문서는 위 원서를 읽고 각 장의 논지와 사실 관계를 한국어로 재구성한 요약본이다.
원문을 그대로 옮긴 번역이 아니며, 인명과 기업명, 수치와 연도는 원서 표기를 따랐다.</p>
<p>4장의 각주에 적어 둔 대로, 원서가 2011년 도호쿠 대지진 뒤의 재해를 태풍이라고 적은 대목은
지진해일로 바로잡아 옮겼다.</p></section>
</body></html>"""

    tmp = ROOT / ".build.html"
    tmp.write_text(page, encoding="utf-8")
    HTML(filename=str(tmp)).write_pdf(str(OUT))
    tmp.unlink()
    print(f"wrote {OUT} ({OUT.stat().st_size/1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
