"""
Shared utilities for professional Opella-style SOP PDF generation.
Extracted from sop_order_management.py so all professional PDF generators
can import a single _SopPdf base class and design tokens.
"""
from fpdf import FPDF

# ── Design tokens ──────────────────────────────────────────────────────────────
FONT     = "Helvetica"
C_NAVY   = (26,  47,  80)      # Opella dark navy
C_BLUE   = (54, 101, 152)      # Section heading blue
C_ACCENT = ( 0, 122, 195)      # Rule / accent line
C_GRAY   = (110, 110, 110)     # Secondary text
C_LGRAY  = (242, 244, 247)     # Alternating row fill
C_NOTE   = (230, 241, 252)     # Note box fill
C_WHITE  = (255, 255, 255)
C_BLACK  = (  0,   0,   0)

# Sanofi-heritage brand colour (dark indigo) for historical Sanofi docs
C_SANOFI = (40, 30, 100)

_SUBS = {
    "—": " - ", "–": " - ",
    "'": "'",   "'": "'",
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "…": "...", "€": "EUR",
}


def _s(t: str) -> str:
    """Sanitise to Latin-1 (built-in fpdf fonts only support ISO-8859-1)."""
    for k, v in _SUBS.items():
        t = t.replace(k, v)
    return t


# ── Base PDF class ─────────────────────────────────────────────────────────────

class _SopPdf(FPDF):
    """
    Professional SOP/policy PDF with:
    - Cover page (navy header/footer bars, metadata grid)
    - Running header (page 2+): doc ref + classification
    - Running footer (page 2+): version / date / page number
    - h1/h2/h3 heading hierarchy that auto-registers TOC entries
    - para / bullets / numbered / note / table layout primitives
    - table() with multi-line cell wrapping

    Parameters
    ----------
    org_name : str
        Organisation brand name shown on cover (default "Opella").
    org_sub : str
        Organisation sub-line shown on cover (default "Consumer Healthcare").
    brand_color : tuple or None
        RGB tuple for the cover bars and fill (default C_NAVY).
    """

    def __init__(self, ref, title, subtitle, version, eff_date, classification,
                 doc_owner, proc_owner, review_date,
                 org_name="Opella", org_sub="Consumer Healthcare",
                 brand_color=None):
        super().__init__("P", "mm", "A4")
        self.ref = ref
        self._title = _s(title)
        self._subtitle = _s(subtitle)
        self.version = version
        self.eff_date = eff_date
        self.classification = classification
        self.doc_owner = doc_owner
        self.proc_owner = proc_owner
        self.review_date = review_date
        self.org_name = org_name
        self.org_sub = org_sub
        self._brand = brand_color if brand_color is not None else C_NAVY
        self.set_margins(22, 30, 20)
        self.set_auto_page_break(True, 22)

    # ── Running header / footer ────────────────────────────────────────────────

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font(FONT, "", 7)
        self.set_text_color(*C_GRAY)
        self.cell(0, 4,
                  f"{self.org_name}  |  {self.ref}  |  {self.classification}",
                  align="L")
        self.set_x(self.l_margin)
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), 190, self.get_y())
        self.ln(4)
        self.set_text_color(*C_BLACK)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-14)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), 190, self.get_y())
        self.ln(1)
        self.set_font(FONT, "", 7)
        self.set_text_color(*C_GRAY)
        self.cell(0, 5,
                  f"Version {self.version}  |  Effective: {self.eff_date}"
                  f"  |  {self.doc_owner}  |  Page {self.page_no()}",
                  align="C")
        self.set_text_color(*C_BLACK)

    # ── Cover page ─────────────────────────────────────────────────────────────

    def cover(self):
        self.add_page()
        self.set_auto_page_break(False)   # keep footer bar on this page

        # Classification bar across top
        self.set_y(0)
        self.set_fill_color(*self._brand)
        self.set_text_color(*C_WHITE)
        self.set_font(FONT, "B", 8)
        self.cell(0, 10, f"   {self.classification}", fill=True, ln=True)

        self.set_y(32)
        # Brand wordmark
        self.set_font(FONT, "B", 34)
        self.set_text_color(*self._brand)
        self.cell(0, 14, self.org_name, ln=True)
        self.set_font(FONT, "", 10)
        self.set_text_color(*C_GRAY)
        self.cell(0, 5, self.org_sub, ln=True)
        self.ln(10)
        # Accent rule
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(1.4)
        self.line(22, self.get_y(), 155, self.get_y())
        self.set_line_width(0.2)
        self.ln(12)
        # Document type label
        self.set_font(FONT, "", 9)
        self.set_text_color(*C_BLUE)
        self.cell(0, 5, _s(self._subtitle.split("|")[0].strip().upper())
                  if "|" not in self._subtitle else
                  self._subtitle.split("|")[0].strip().upper(), ln=True)
        self.ln(4)
        # Document title
        self.set_font(FONT, "B", 22)
        self.set_text_color(*self._brand)
        self.multi_cell(0, 11, self._title)
        self.ln(2)
        self.set_font(FONT, "", 12)
        self.set_text_color(*C_BLUE)
        self.cell(0, 7, self._subtitle, ln=True)
        self.ln(20)
        # Metadata grid
        meta = [
            ("Document Reference",  self.ref),
            ("Version",             self.version),
            ("Effective Date",      self.eff_date),
            ("Review Date",         self.review_date),
            ("Document Owner",      self.doc_owner),
            ("Process Owner",       self.proc_owner),
            ("Document Status",     "APPROVED"),
            ("Classification",      self.classification),
        ]
        self.set_draw_color(210, 210, 210)
        for label, value in meta:
            self.set_font(FONT, "", 8.5)
            self.set_text_color(*C_GRAY)
            self.cell(60, 7.5, label, border="B")
            self.set_font(FONT, "B", 8.5)
            self.set_text_color(*C_BLACK)
            self.cell(0, 7.5, value, border="B", ln=True)
        # Bottom classification footer bar
        self.set_y(-18)
        self.set_fill_color(*self._brand)
        self.set_text_color(*C_WHITE)
        self.set_font(FONT, "", 7)
        self.cell(0, 10,
                  f"   {self.org_name}  |  {self.ref}  |  {self.classification}"
                  f"  |  Version {self.version}  |  Effective {self.eff_date}",
                  fill=True, ln=True)
        self.set_auto_page_break(True, 22)  # restore for body pages

    # ── Layout primitives ──────────────────────────────────────────────────────

    def h1(self, text):
        """Top-level section heading — registers in TOC (level 0)."""
        text = _s(text)
        if self.get_y() > 240:
            self.add_page()
        self.ln(3)
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*self._brand)
        self.rect(x, y + 1.5, 3.5, 7, "F")
        self.set_font(FONT, "B", 12)
        self.set_text_color(*self._brand)
        self.set_x(x + 7)
        self.cell(0, 10, text, ln=True)
        self.set_draw_color(210, 210, 210)
        self.line(self.l_margin, self.get_y(), 190, self.get_y())
        self.ln(3)
        self.set_text_color(*C_BLACK)
        self.start_section(text, level=0)

    def h2(self, text):
        """Sub-section heading — registers in TOC (level 1)."""
        text = _s(text)
        if self.get_y() > 255:
            self.add_page()
        self.ln(1)
        self.set_font(FONT, "B", 10.5)
        self.set_text_color(*C_BLUE)
        self.cell(0, 7, text, ln=True)
        self.ln(0.5)
        self.set_text_color(*C_BLACK)
        self.start_section(text, level=1)

    def h3(self, text):
        """Third-level heading (no TOC entry)."""
        text = _s(text)
        self.set_font(FONT, "B", 9.5)
        self.set_text_color(*C_BLACK)
        self.cell(0, 6, text, ln=True)
        self.ln(0.5)

    def para(self, text):
        self.set_font(FONT, "", 9.5)
        self.set_text_color(*C_BLACK)
        for block in _s(text).strip().split("\n\n"):
            self.multi_cell(0, 5.4, block.strip())
            self.ln(2)
        self.ln(0.5)

    def bullets(self, items, indent_mm=5):
        self.set_font(FONT, "", 9.5)
        self.set_text_color(*C_BLACK)
        for item in items:
            self.set_x(self.l_margin + indent_mm)
            self.cell(5, 5.5, "-")
            self.multi_cell(0, 5.5, _s(item))
        self.ln(2)

    def numbered(self, items, indent_mm=5):
        self.set_font(FONT, "", 9.5)
        self.set_text_color(*C_BLACK)
        for i, item in enumerate(items, 1):
            self.set_x(self.l_margin + indent_mm)
            self.cell(7, 5.5, f"{i}.")
            self.multi_cell(0, 5.5, _s(item))
        self.ln(2)

    def note(self, title, text):
        """Shaded note / important callout box."""
        self.set_fill_color(*C_NOTE)
        self.set_draw_color(*C_BLUE)
        self.set_font(FONT, "B", 8.5)
        self.set_text_color(*self._brand)
        self.cell(0, 7, f"  {_s(title)}", fill=True, ln=True)
        self.set_font(FONT, "", 8.5)
        self.set_text_color(*C_BLACK)
        for line in _s(text).strip().split("\n"):
            self.set_x(self.l_margin + 4)
            self.multi_cell(0, 5, line.strip())
        self.ln(4)

    def table(self, headers, rows, widths=None):
        """Formatted table with dark header row, alternating fill, and wrapping cells."""
        if widths is None:
            w = 168 / len(headers)
            widths = [w] * len(headers)
        line_h = 5.0
        pad_x = 1.5
        pad_y = 1.0

        # Header row (single-line)
        self.set_fill_color(*self._brand)
        self.set_text_color(*C_WHITE)
        self.set_font(FONT, "B", 8)
        for h, w in zip(headers, widths):
            self.cell(w, 7, f"  {_s(str(h))}", fill=True)
        self.ln()

        # Data rows with multi-line wrapping
        self.set_font(FONT, "", 8.5)
        self.set_text_color(*C_BLACK)
        for i, row in enumerate(rows):
            fill = i % 2 == 0

            # Calculate required height for each cell
            cell_heights = []
            for val, w in zip(row, widths):
                text = _s(str(val))
                avail = w - pad_x * 2
                if avail <= 0:
                    cell_heights.append(7)
                    continue
                lines = 0
                for segment in text.split("\n"):
                    seg_lines = 1
                    cur_w = 0.0
                    for word in (segment.split(" ") if segment.strip() else []):
                        ww = self.get_string_width(word + " ")
                        if cur_w + ww > avail and cur_w > 0:
                            seg_lines += 1
                            cur_w = ww
                        else:
                            cur_w += ww
                    lines += seg_lines
                cell_heights.append(max(1, lines) * line_h + pad_y * 2)
            row_h = max(max(cell_heights), 7)

            # Page break if row would overflow
            if self.get_y() + row_h > self.h - self.b_margin:
                self.add_page()

            y0 = self.get_y()

            # Alternating background fill
            if fill:
                self.set_fill_color(*C_LGRAY)
                self.rect(self.l_margin, y0, sum(widths), row_h, "F")

            # Render text in each cell
            x = self.l_margin
            for val, w in zip(row, widths):
                self.set_xy(x + pad_x, y0 + pad_y)
                self.multi_cell(w - pad_x * 2, line_h, _s(str(val)))
                x += w

            self.set_y(y0 + row_h)

        self.ln(4)
        self.set_fill_color(*C_WHITE)


# ── TOC renderer ───────────────────────────────────────────────────────────────

def _render_toc(pdf, outline):
    """Renders top-level (level 0) sections only - fits on a single page."""
    pdf.set_font(FONT, "B", 12)
    pdf.set_text_color(*C_NAVY)
    pdf.cell(0, 9, "Table of Contents", ln=True)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    for section in outline:
        if section.level != 0:
            continue
        pdf.set_font(FONT, "B", 9.5)
        pdf.set_text_color(*C_NAVY)
        pdf.set_x(pdf.l_margin)
        name = _s(section.name)
        page_str = str(section.page_number)
        link = pdf.add_link()
        pdf.set_link(link, page=section.page_number)
        pdf.cell(154, 7, name, link=link)
        pdf.cell(14, 7, page_str, align="R", ln=True)

    pdf.set_text_color(*C_BLACK)
