from fpdf import FPDF

FONT_FAMILY = "Helvetica"

# Built-in fpdf2 fonts use Latin-1 (ISO-8859-1). Replace chars outside that range.
_CHAR_MAP = {
    "—": " - ",   # em dash
    "–": " - ",   # en dash
    "‘": "'",     # left single quote
    "’": "'",     # right single quote
    "“": '"',     # left double quote
    "”": '"',     # right double quote
    "…": "...",   # ellipsis
}


def _safe(text: str) -> str:
    for char, replacement in _CHAR_MAP.items():
        text = text.replace(char, replacement)
    return text


class OpellaDoc:
    """Generates a single-column Opella-branded PDF document."""

    def __init__(self, title: str, subtitle: str, classification: str = "INTERNAL"):
        self.title = title
        self.subtitle = subtitle
        self.classification = classification
        self._pdf = FPDF(orientation="P", unit="mm", format="A4")
        self._pdf.set_margins(left=20, top=20, right=20)
        self._pdf.set_auto_page_break(auto=True, margin=20)
        self._sections: list[tuple[str, str]] = []

    def add_section(self, heading: str, body: str) -> None:
        self._sections.append((heading, body))

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Appends a table to the last section's body (stored as special marker)."""
        self._sections.append(("__table__", (headers, rows)))

    def save(self, path: str) -> None:
        self._pdf.add_page()
        self._render_cover()
        for item in self._sections:
            heading, content = item
            if heading == "__table__":
                self._render_table(content[0], content[1])
            else:
                self._render_section(heading, content)
        self._pdf.output(path)

    # ── private ──────────────────────────────────────────────────────────────

    def _render_cover(self) -> None:
        p = self._pdf
        p.set_font(FONT_FAMILY, "B", 18)
        p.cell(0, 10, "Opella", ln=True)
        p.set_font(FONT_FAMILY, "", 11)
        p.set_text_color(100, 100, 100)
        p.cell(0, 6, _safe(self.classification), ln=True)
        p.ln(6)
        p.set_text_color(0, 0, 0)
        p.set_font(FONT_FAMILY, "B", 15)
        p.multi_cell(0, 8, _safe(self.title))
        p.set_font(FONT_FAMILY, "", 11)
        p.set_text_color(80, 80, 80)
        p.cell(0, 7, _safe(self.subtitle), ln=True)
        p.ln(8)
        p.set_draw_color(200, 200, 200)
        p.line(20, p.get_y(), 190, p.get_y())
        p.ln(6)
        p.set_text_color(0, 0, 0)

    def _render_section(self, heading: str, body: str) -> None:
        p = self._pdf
        p.set_font(FONT_FAMILY, "B", 12)
        p.multi_cell(0, 7, _safe(heading))
        p.ln(1)
        p.set_font(FONT_FAMILY, "", 10)
        for paragraph in body.split("\n\n"):
            p.multi_cell(0, 5.5, _safe(paragraph.strip()))
            p.ln(3)
        p.ln(2)

    def _render_table(self, headers: list[str], rows: list[list[str]]) -> None:
        p = self._pdf
        col_w = 170 / max(len(headers), 1)
        p.set_font(FONT_FAMILY, "B", 9)
        p.set_fill_color(240, 240, 240)
        for h in headers:
            p.cell(col_w, 7, _safe(h), border=1, fill=True)
        p.ln()
        p.set_font(FONT_FAMILY, "", 9)
        for row in rows:
            for cell in row:
                p.cell(col_w, 6, _safe(str(cell)), border=1)
            p.ln()
        p.ln(3)
