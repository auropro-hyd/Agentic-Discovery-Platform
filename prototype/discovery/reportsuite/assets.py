"""CSS/JS for the client-facing report suite. Restrained corporate palette; a single calm
accent for emphasis only (no red/amber status colours anywhere)."""

CSS = """
:root{ --ink:#1a2230; --muted:#5b6776; --line:#e3e8ee; --bg:#f7f9fb;
       --accent:#1f6feb; --accent-soft:#eaf1fe; --panel:#ffffff; }
*{ box-sizing:border-box; }
body{ margin:0; font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
      color:var(--ink); background:var(--bg); line-height:1.55; }
.layout{ display:flex; min-height:100vh; }
.sidebar{ width:270px; flex:0 0 270px; background:#0f1b2d; color:#cdd7e4; padding:1.5rem 1rem;
          position:sticky; top:0; height:100vh; overflow:auto; }
.sidebar h1{ font-size:1rem; color:#fff; margin:0 0 .25rem; }
.sidebar .sub{ font-size:.78rem; color:#8da2bd; margin-bottom:1.5rem; }
.sidebar a{ display:block; color:#cdd7e4; text-decoration:none; padding:.55rem .7rem;
            border-radius:7px; font-size:.9rem; margin-bottom:.15rem; }
.sidebar a:hover{ background:#1b2c44; }
.sidebar a.active{ background:var(--accent); color:#fff; }
.sidebar .num{ color:#6f86a6; font-variant-numeric:tabular-nums; margin-right:.5rem; }
.content{ flex:1; padding:2.5rem 3rem; max-width:920px; }
.content h1{ font-size:1.7rem; margin:0 0 .3rem; }
.content h2{ font-size:1.25rem; margin:2.2rem 0 .6rem; padding-bottom:.3rem;
             border-bottom:1px solid var(--line); }
.content h3{ font-size:1.05rem; margin:1.6rem 0 .4rem; }
.lede{ color:var(--muted); margin:0 0 1.5rem; }
table{ border-collapse:collapse; width:100%; margin:1rem 0; background:var(--panel); font-size:.9rem; }
th,td{ border:1px solid var(--line); padding:.55rem .7rem; text-align:left; vertical-align:top; }
th{ background:#f0f3f7; font-weight:600; }
.prov{ color:var(--muted); font-size:.82rem; font-style:italic; }
.metric{ display:inline-block; background:var(--accent-soft); color:#0a4bbd; font-weight:600;
         padding:.05rem .4rem; border-radius:5px; }
.card{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
       padding:1.2rem 1.4rem; margin:1.2rem 0; }
.pattern{ display:inline-block; font-size:.72rem; letter-spacing:.04em; text-transform:uppercase;
          color:var(--accent); border:1px solid var(--accent); border-radius:20px;
          padding:.1rem .6rem; margin-left:.5rem; vertical-align:middle; }
.ba-grid{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:1rem 0; }
.ba-grid .col h4{ margin:.2rem 0 .5rem; font-size:.95rem; }
.ba-grid .before{ border-left:3px solid #c9d2dd; padding-left:.9rem; }
.ba-grid .after{ border-left:3px solid var(--accent); padding-left:.9rem; }
.step{ margin:.5rem 0; }
.step .who{ color:var(--muted); font-size:.82rem; }
.failpoint{ color:#8a5a00; background:#fdf4e3; border-radius:5px; padding:.05rem .35rem;
            font-size:.82rem; display:inline-block; margin:.15rem .15rem 0 0; }
.matrix{ display:grid; grid-template-columns:1fr 1fr; grid-auto-rows:150px; gap:.5rem; margin:1.2rem 0; }
.quad{ border:1px solid var(--line); border-radius:9px; padding:.7rem .8rem; background:var(--panel); }
.quad h4{ margin:0 0 .4rem; font-size:.82rem; color:var(--muted); text-transform:uppercase;
          letter-spacing:.03em; }
.quad.do_first{ background:var(--accent-soft); }
.chip{ display:inline-block; background:#fff; border:1px solid var(--accent); color:#0a4bbd;
       border-radius:6px; padding:.15rem .5rem; margin:.2rem .2rem 0 0; font-size:.84rem; }
.horizon{ border-left:3px solid var(--accent); padding:.2rem 0 .2rem 1rem; margin:1rem 0; }
.horizon .win{ color:var(--muted); font-size:.85rem; }
.badge-note{ font-size:.82rem; color:var(--muted); }
.flow-wrap{ background:linear-gradient(180deg,#fbfdff,#f5f8fc); border:1px solid var(--line);
            border-radius:12px; padding:1.1rem 1.2rem .9rem; margin:1.2rem 0; overflow-x:auto; }
.flow-cap{ font-size:.8rem; color:var(--muted); text-transform:uppercase; letter-spacing:.05em;
           margin-bottom:.7rem; font-weight:600; }
.flow{ display:block; max-width:820px; }
.srcdoc{ white-space:pre-wrap; word-break:break-word; background:var(--panel);
         border:1px solid var(--line); border-radius:8px; padding:1rem; font-size:.82rem;
         line-height:1.5; max-height:none; }
ul{ margin:.4rem 0 .8rem; } li{ margin:.2rem 0; }
@media print{ .sidebar{ display:none; } .content{ max-width:none; } }
@media (max-width:760px){ .layout{ flex-direction:column; } .sidebar{ width:100%; height:auto;
   position:static; } .ba-grid,.matrix{ grid-template-columns:1fr; } .content{ padding:1.5rem; } }
"""

JS = ""  # no JS needed for standalone pages
