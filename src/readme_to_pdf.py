"""Convert README.md to READ-THIS-FIRST.pdf using reportlab."""

import re
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Preformatted, ListFlowable, ListItem, Table, TableStyle,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

BASE = pathlib.Path(__file__).parent.parent
README = BASE / "README.md"
OUTPUT = BASE / "READ-THIS-FIRST.pdf"

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
NAVY   = colors.HexColor("#1a1a4e")
BLUE   = colors.HexColor("#0050b3")
GREY   = colors.HexColor("#555555")
LGREY  = colors.HexColor("#f4f4f8")
WHITE  = colors.white

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
BASE_STYLES = getSampleStyleSheet()

def make_styles():
    s = {}

    def add(name, **kw):
        s[name] = ParagraphStyle(name, **kw)

    add("h1",
        fontName="Helvetica-Bold", fontSize=22, textColor=NAVY,
        spaceAfter=10, spaceBefore=16, leading=28)
    add("h2",
        fontName="Helvetica-Bold", fontSize=15, textColor=NAVY,
        spaceAfter=6, spaceBefore=14, leading=20,
        borderPad=4)
    add("h3",
        fontName="Helvetica-Bold", fontSize=12, textColor=BLUE,
        spaceAfter=4, spaceBefore=10, leading=16)
    add("h4",
        fontName="Helvetica-Bold", fontSize=11, textColor=GREY,
        spaceAfter=4, spaceBefore=8, leading=14)
    add("body",
        fontName="Helvetica", fontSize=10, textColor=colors.black,
        spaceAfter=6, leading=15)
    add("quote",
        fontName="Helvetica-Oblique", fontSize=10, textColor=GREY,
        spaceAfter=6, leading=15, leftIndent=18,
        borderPad=6)
    add("code_inline",
        fontName="Courier", fontSize=9, textColor=colors.black,
        spaceAfter=6, leading=14)
    add("bullet",
        fontName="Helvetica", fontSize=10, textColor=colors.black,
        spaceAfter=3, leading=14)
    return s


# ---------------------------------------------------------------------------
# Emoji stripping
# ---------------------------------------------------------------------------
EMOJI_MAP = {
    "🧠": "", "⚡": "", "🗺️": "", "✍️": "", "🔍": "", "🏗️": "",
    "🚀": "", "📁": "", "🛠️": "", "📦": "", "💡": "", "📂": "",
    "📊": "", "💬": "", "📋": "", "🗂️": "", "📐": "", "💾": "",
    "💻": "", "▶️": "", "🔧": "", "✅": "[OK]", "📈": "", "🤖": "",
}

def strip_emoji(text: str) -> str:
    for emoji, repl in EMOJI_MAP.items():
        text = text.replace(emoji, repl)
    text = re.sub(r"[\U00010000-\U0010FFFF]", "", text)
    return text


# ---------------------------------------------------------------------------
# Inline markdown → reportlab XML
# ---------------------------------------------------------------------------
def inline_md(text: str) -> str:
    """Convert inline markdown (bold, italic, code, links) to reportlab XML."""
    # Escape XML special chars first (but not & which we'll handle)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold+italic
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="9">\1</font>', text)
    # Links — show text only
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r'<font color="#0050b3">\1</font>', text)
    return text


# ---------------------------------------------------------------------------
# Markdown parser → reportlab flowables
# ---------------------------------------------------------------------------
def parse_markdown(md: str, styles: dict) -> list:
    flowables = []
    lines = md.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Blank line
        if not line.strip():
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^---+$", line.strip()):
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Fenced code block
        if line.strip().startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = "\n".join(code_lines)
            flowables.append(Spacer(1, 4))
            pre = Preformatted(
                code_text,
                ParagraphStyle(
                    "pre",
                    fontName="Courier", fontSize=8, leading=12,
                    backColor=LGREY, borderPad=8,
                    leftIndent=8, rightIndent=8,
                    spaceAfter=6,
                ),
            )
            flowables.append(pre)
            flowables.append(Spacer(1, 4))
            continue

        # Blockquote
        if line.startswith(">"):
            text = line.lstrip("> ").strip()
            flowables.append(Paragraph(inline_md(text), styles["quote"]))
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text = strip_emoji(m.group(2)).strip()
            style_key = f"h{level}" if level <= 4 else "h4"
            flowables.append(Paragraph(inline_md(text), styles[style_key]))
            i += 1
            continue

        # Unordered list
        if re.match(r"^[\-\*\+] ", line):
            items = []
            while i < len(lines) and re.match(r"^[\-\*\+] ", lines[i]):
                item_text = re.sub(r"^[\-\*\+] ", "", lines[i]).strip()
                items.append(ListItem(
                    Paragraph(inline_md(item_text), styles["bullet"]),
                    bulletColor=BLUE, leftIndent=20,
                ))
                i += 1
            flowables.append(ListFlowable(items, bulletType="bullet", bulletFontSize=8))
            continue

        # Ordered list
        if re.match(r"^\d+[\.\)] ", line):
            items = []
            num = 1
            while i < len(lines) and re.match(r"^\d+[\.\)] ", lines[i]):
                item_text = re.sub(r"^\d+[\.\)] ", "", lines[i]).strip()
                items.append(ListItem(
                    Paragraph(inline_md(item_text), styles["bullet"]),
                    leftIndent=20,
                ))
                i += 1
                num += 1
            flowables.append(ListFlowable(items, bulletType="1"))
            continue

        # Markdown table
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|", lines[i + 1].strip()):
            table_rows = []
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(header_cells)
            i += 2  # skip separator row
            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                table_rows.append(cells)
                i += 1
            # Convert to Paragraph objects
            para_rows = []
            for r_idx, row in enumerate(table_rows):
                style = ParagraphStyle(
                    "tcell",
                    fontName="Helvetica-Bold" if r_idx == 0 else "Helvetica",
                    fontSize=9, leading=13,
                    textColor=WHITE if r_idx == 0 else colors.black,
                )
                para_rows.append([Paragraph(inline_md(c), style) for c in row])
            col_count = max(len(r) for r in para_rows)
            available = 17 * cm
            col_w = available / col_count
            t = Table(para_rows, colWidths=[col_w] * col_count)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGREY]),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            flowables.append(Spacer(1, 6))
            flowables.append(t)
            flowables.append(Spacer(1, 6))
            continue

        # Plain paragraph (possibly multi-line)
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,4} |>|[\-\*\+] |\d+[\.\)] |```|---)", lines[i]
        ) and "|" not in lines[i]:
            para_lines.append(lines[i])
            i += 1
        text = " ".join(para_lines)
        flowables.append(Paragraph(inline_md(text), styles["body"]))

    return flowables


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    md_text = README.read_text(encoding="utf-8")
    md_text = strip_emoji(md_text)

    styles = make_styles()

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
        title="Data Intelligence Researcher — Read This First",
        author="Claude Code",
    )

    flowables = parse_markdown(md_text, styles)
    doc.build(flowables)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
