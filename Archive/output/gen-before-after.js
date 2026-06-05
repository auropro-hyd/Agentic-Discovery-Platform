const pptxgen = require("/opt/homebrew/lib/node_modules/pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Discovery Engagement: Before & After";

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

// ── Palette ───────────────────────────────────────────────────────────────────
const NAVY      = "1E2761";
const WHITE     = "FFFFFF";
const AMBER     = "D97706";
const AMBER_BG  = "FEF3C7";
const AMBER_DK  = "92400E";
const BLUE      = "2563EB";
const BLUE_BG   = "EFF6FF";
const BLUE_DK   = "1E40AF";
const GREEN     = "16A34A";
const GREEN_BG  = "F0FDF4";
const GREEN_DK  = "14532D";
const PURPLE    = "7C3AED";
const PURPLE_BG = "F5F3FF";
const PURPLE_DK = "4C1D95";
const GREY      = "9CA3AF";
const GREY_BG   = "F3F4F6";
const GREY_DK   = "6B7280";
const TEXT      = "1A1A1A";
const MUTED     = "6B7280";

// ── Title band ────────────────────────────────────────────────────────────────
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.55,
  fill: { color: NAVY }, line: { color: NAVY },
});
slide.addText("Discovery Engagement: Before & After", {
  x: 0.4, y: 0.04, w: 8.5, h: 0.47,
  fontSize: 22, fontFace: "Georgia", bold: true,
  color: WHITE, valign: "middle", margin: 0,
});

// ── Traditional section ───────────────────────────────────────────────────────
slide.addText("TRADITIONAL CONSULTING  ·  10–14 WEEKS", {
  x: 0.4, y: 0.65, w: 5.5, h: 0.22,
  fontSize: 9, fontFace: "Calibri", bold: true,
  color: AMBER, charSpacing: 2.5, valign: "middle", margin: 0,
});

const TY = 1.10;

slide.addShape(pres.shapes.LINE, {
  x: 0.4, y: TY, w: 9.2, h: 0,
  line: { color: AMBER, width: 2 },
});

const tradNodes = [
  { x: 0.40, fill: AMBER_BG, border: AMBER,  l1: "Kickoff &",      l2: "workshops",   d: "Wk 1–5  ·  ~35 hrs" },
  { x: 2.72, fill: AMBER_BG, border: AMBER,  l1: "Document",       l2: "handover",    d: "Wk 3  ·  2 hrs" },
  { x: 5.05, fill: GREY_BG,  border: GREY,   l1: "Waiting...",     l2: "follow-ups",  d: "Wk 5–11" },
  { x: 7.37, fill: AMBER_BG, border: AMBER,  l1: "Draft review &", l2: "revisions",   d: "Wk 12–13  ·  7 hrs" },
  { x: 9.40, fill: BLUE_BG,  border: BLUE,   l1: "Final",          l2: "delivery",    d: "Wk 14  ·  1 report" },
];

tradNodes.forEach((n) => {
  const r = 0.16;
  slide.addShape(pres.shapes.OVAL, {
    x: n.x - r, y: TY - r, w: r * 2, h: r * 2,
    fill: { color: n.fill }, line: { color: n.border, width: 1.5 },
  });
  const lx = Math.max(0.05, Math.min(n.x - 0.65, 8.70));
  const lw = 1.32;
  slide.addText(n.l1, {
    x: lx, y: TY + 0.20, w: lw, h: 0.19,
    fontSize: 8, fontFace: "Calibri", bold: true, color: TEXT,
    align: "center", valign: "top", margin: 0,
  });
  slide.addText(n.l2, {
    x: lx, y: TY + 0.39, w: lw, h: 0.19,
    fontSize: 8, fontFace: "Calibri", bold: true, color: TEXT,
    align: "center", valign: "top", margin: 0,
  });
  slide.addText(n.d, {
    x: lx, y: TY + 0.60, w: lw, h: 0.18,
    fontSize: 7.5, fontFace: "Calibri", color: MUTED,
    align: "center", valign: "top", margin: 0,
  });
});

// ── Platform section ──────────────────────────────────────────────────────────
const PY = 2.52;

slide.addText("AUROPRO PLATFORM  ·  5–6 DAYS", {
  x: 0.4, y: PY - 0.45, w: 5.0, h: 0.22,
  fontSize: 9, fontFace: "Calibri", bold: true,
  color: BLUE, charSpacing: 2.5, valign: "middle", margin: 0,
});

// Compressed timeline line (left ~55%)
slide.addShape(pres.shapes.LINE, {
  x: 0.4, y: PY, w: 5.5, h: 0,
  line: { color: BLUE, width: 2 },
});

// Right-side callout (empty space = compression is the message)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 6.35, y: PY - 0.52, w: 3.25, h: 1.04,
  fill: { color: BLUE_BG }, line: { color: BLUE, width: 1 },
});
slide.addText("While the platform works,\nyour team does something else.", {
  x: 6.45, y: PY - 0.50, w: 3.05, h: 1.00,
  fontSize: 9.5, fontFace: "Calibri", italic: true,
  color: BLUE_DK, align: "center", valign: "middle", margin: 0,
});

const platNodes = [
  { x: 0.50, fill: AMBER_BG,  border: AMBER,  l1: "Strategy",  l2: "alignment",  d: "Day 0  ·  1 hr" },
  { x: 1.50, fill: AMBER_BG,  border: AMBER,  l1: "Document",  l2: "drop",       d: "Day 0  ·  30 min" },
  { x: 2.50, fill: GREEN_BG,  border: GREEN,  l1: "Platform",  l2: "analyses",   d: "Day 1  ·  AuroPro" },
  { x: 3.50, fill: PURPLE_BG, border: PURPLE, l1: "Gap",       l2: "resolution", d: "Day 2–3  ·  2–3 hrs" },
  { x: 4.50, fill: GREEN_BG,  border: GREEN,  l1: "Reports",   l2: "generated",  d: "Day 3–4  ·  AuroPro" },
  { x: 5.50, fill: PURPLE_BG, border: PURPLE, l1: "Review &",  l2: "sign-off",   d: "Day 5–6  ·  3 hrs" },
];

platNodes.forEach((n) => {
  const r = 0.16;
  slide.addShape(pres.shapes.OVAL, {
    x: n.x - r, y: PY - r, w: r * 2, h: r * 2,
    fill: { color: n.fill }, line: { color: n.border, width: 1.5 },
  });
  const lx = Math.max(0.05, n.x - 0.50);
  const lw = 1.00;
  slide.addText(n.l1, {
    x: lx, y: PY + 0.20, w: lw, h: 0.19,
    fontSize: 8, fontFace: "Calibri", bold: true, color: TEXT,
    align: "center", valign: "top", margin: 0,
  });
  slide.addText(n.l2, {
    x: lx, y: PY + 0.39, w: lw, h: 0.19,
    fontSize: 8, fontFace: "Calibri", bold: true, color: TEXT,
    align: "center", valign: "top", margin: 0,
  });
  slide.addText(n.d, {
    x: lx, y: PY + 0.60, w: lw, h: 0.18,
    fontSize: 7.5, fontFace: "Calibri", color: MUTED,
    align: "center", valign: "top", margin: 0,
  });
});

// ── Legend ────────────────────────────────────────────────────────────────────
const LY = 3.42;

slide.addText("KEY", {
  x: 0.4, y: LY, w: 0.44, h: 0.18,
  fontSize: 7.5, fontFace: "Calibri", bold: true,
  color: MUTED, charSpacing: 2, margin: 0,
});

const legItems = [
  { fill: AMBER_BG,  border: AMBER,  label: "Your time required" },
  { fill: GREEN_BG,  border: GREEN,  label: "AuroPro only" },
  { fill: PURPLE_BG, border: PURPLE, label: "Joint decision point" },
  { fill: GREY_BG,   border: GREY,   label: "Waiting / unstructured" },
];

legItems.forEach((item, i) => {
  const lx = 0.92 + i * 2.08;
  slide.addShape(pres.shapes.OVAL, {
    x: lx, y: LY + 0.02, w: 0.14, h: 0.14,
    fill: { color: item.fill }, line: { color: item.border, width: 1 },
  });
  slide.addText(item.label, {
    x: lx + 0.20, y: LY, w: 1.82, h: 0.18,
    fontSize: 8, fontFace: "Calibri", color: MUTED,
    valign: "middle", margin: 0,
  });
});

// ── Comparison cards ──────────────────────────────────────────────────────────
const CY = 3.70;
const CH = 0.80;

// Left card — Traditional
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.40, y: CY, w: 4.10, h: CH,
  fill: { color: "FFFBF0" }, line: { color: AMBER, width: 1.5 },
});
slide.addText("~55 hrs  ·  14 weeks", {
  x: 0.52, y: CY + 0.06, w: 3.86, h: 0.28,
  fontSize: 13, fontFace: "Georgia", bold: true, color: AMBER_DK,
  align: "left", valign: "middle", margin: 0,
});
slide.addText("Your team as primary data source: interviews, workshops, document reviews, draft approval.", {
  x: 0.52, y: CY + 0.36, w: 3.86, h: 0.38,
  fontSize: 8.5, fontFace: "Calibri", color: TEXT,
  align: "left", valign: "top", margin: 0,
});

// Arrow
slide.addText("→", {
  x: 4.60, y: CY + 0.22, w: 0.70, h: 0.36,
  fontSize: 20, fontFace: "Georgia", color: MUTED,
  align: "center", valign: "middle", margin: 0,
});

// Right card — Platform
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.40, y: CY, w: 4.20, h: CH,
  fill: { color: "F0F5FF" }, line: { color: BLUE, width: 1.5 },
});
slide.addText("~8 hrs  ·  5–6 days", {
  x: 5.52, y: CY + 0.06, w: 3.96, h: 0.28,
  fontSize: 13, fontFace: "Georgia", bold: true, color: BLUE_DK,
  align: "left", valign: "middle", margin: 0,
});
slide.addText("Your team for decisions only: direction-setting, targeted gap questions, findings review, sign-off.", {
  x: 5.52, y: CY + 0.36, w: 3.96, h: 0.38,
  fontSize: 8.5, fontFace: "Calibri", color: TEXT,
  align: "left", valign: "top", margin: 0,
});

// ── Verdict bar ───────────────────────────────────────────────────────────────
const VY = 4.62;
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: VY, w: 10, h: 1.005,
  fill: { color: NAVY }, line: { color: NAVY },
});
slide.addText("The shift isn't just speed — it's what your time is for.", {
  x: 0.4, y: VY + 0.09, w: 7.1, h: 0.825,
  fontSize: 13, fontFace: "Georgia", italic: true,
  color: WHITE, valign: "middle", margin: 0,
});
slide.addText("~85% less\nclient time", {
  x: 7.6, y: VY + 0.09, w: 2.0, h: 0.825,
  fontSize: 13, fontFace: "Georgia", bold: true,
  color: "93C5FD", align: "right", valign: "middle", margin: 0,
});

pres.writeFile({ fileName: "output/before-after-discovery.pptx" }).then(() => {
  console.log("Done: output/before-after-discovery.pptx");
});
