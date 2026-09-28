"""Build docs/index.html from data/conferences.yml. Past events are dropped automatically."""
import datetime as dt
import html
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPICS = {"eo": "Earth observation", "methane": "Methane", "ghg": "Greenhouse gases",
          "emissions": "Emissions", "ai": "ML / AI"}
REGIONS = {"europe": "Europe", "world": "Rest of world"}
e = html.escape


def as_date(v):
    return v if isinstance(v, dt.date) else dt.date.fromisoformat(str(v))


def load():
    items = yaml.safe_load((ROOT / "data" / "conferences.yml").read_text(encoding="utf-8")) or []
    today = dt.date.today()
    out = []
    for c in items:
        start = as_date(c["start"])
        end = as_date(c.get("end") or start)
        if end >= today:
            out.append({**c, "start": start, "end": end})
    return sorted(out, key=lambda c: c["start"])


def fmt_dates(s, en):
    if s == en:
        return f"{s.day} {s:%b %Y}"
    if s.year == en.year and s.month == en.month:
        return f"{s.day}–{en.day} {s:%b %Y}"
    if s.year == en.year:
        return f"{s.day} {s:%b} – {en.day} {en:%b %Y}"
    return f"{s.day} {s:%b %Y} – {en.day} {en:%b %Y}"


def row(c):
    tags = "".join(f'<span class="tag">{e(TOPICS.get(t, t))}</span>' for t in c.get("topics", []))
    deadline = f'<p class="dl">Abstract deadline: {e(str(c["deadline"]))}</p>' if c.get("deadline") else ""
    note = f'<p class="note">{e(c["note"])}</p>' if c.get("note") else ""
    place = ", ".join(x for x in (c.get("city"), c.get("country")) if x)
    search = " ".join([c["name"], place, " ".join(c.get("topics", []))]).lower()
    return (
        f'<li class="ev" data-region="{e(c.get("region", "world"))}" '
        f'data-topics="{e(" ".join(c.get("topics", [])))}" data-search="{e(search)}">\n'
        f'  <time datetime="{c["start"].isoformat()}">{e(fmt_dates(c["start"], c["end"]))}</time>\n'
        f'  <div><h3><a href="{e(c["url"])}" rel="noopener">{e(c["name"])}</a></h3>\n'
        f'  <p class="place">{e(place)}</p>{note}{deadline}<p class="tags">{tags}</p></div>\n</li>'
    )


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Earth observation &amp; emissions conferences</title>
<style>
:root{--bg:#eef2f5;--ink:#14212b;--mute:#586773;--line:#cbd5dc;--card:#fff;--acc:#0b6e79;--hot:#c2410c}
@media (prefers-color-scheme:dark){:root{--bg:#0f1a21;--ink:#e6edf1;--mute:#93a3ae;--line:#26363f;--card:#16252e;--acc:#5cc2cc;--hot:#fb923c}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 "Iowan Old Style","Palatino Linotype",Georgia,serif}
main{max-width:52rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.15;margin:0 0 .5rem}
.lead{color:var(--mute);margin:0 0 1.75rem;max-width:40rem}
.controls{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1.25rem}
.controls input,.controls select{font:inherit;padding:.5rem .7rem;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.controls input{flex:1 1 14rem}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
ul{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.ev{display:grid;grid-template-columns:9.5rem 1fr;gap:1rem;padding:1.1rem 0;border-bottom:1px solid var(--line)}
.ev[hidden]{display:none}
time{font-family:system-ui,sans-serif;font-size:.9rem;font-weight:600;color:var(--hot)}
h3{margin:0;font-size:1.15rem;line-height:1.3}
a{color:var(--ink);text-decoration-color:var(--acc);text-underline-offset:3px}
a:hover{color:var(--acc)}
.place,.note,.dl{margin:.15rem 0 0;color:var(--mute);font-size:.95rem}
.tags{margin:.5rem 0 0;display:flex;flex-wrap:wrap;gap:.35rem}
.tag{font:.78rem system-ui,sans-serif;border:1px solid var(--line);border-radius:99px;padding:.1rem .6rem;color:var(--mute)}
.empty{padding:1.5rem 0;color:var(--mute)}
footer{margin-top:2rem;color:var(--mute);font-size:.85rem}
@media (max-width:560px){.ev{grid-template-columns:1fr;gap:.25rem}}
</style></head>
<body><main>
<h1>Earth observation, methane &amp; emissions conferences</h1>
<p class="lead">Upcoming conferences on Earth observation, greenhouse gases, methane, emissions and machine learning for the Earth system. Europe first, plus major events worldwide.</p>
<div class="controls">
<input id="q" type="search" placeholder="Search name, city, country" aria-label="Search">
<select id="region" aria-label="Region"><option value="">All regions</option>__REGIONS__</select>
<select id="topic" aria-label="Topic"><option value="">All topics</option>__TOPICS__</select>
</div>
<ul id="list">__ROWS__</ul>
<p class="empty" id="empty" hidden>No conferences match these filters.</p>
<footer>__COUNT__ upcoming events. Updated __TODAY__. Past events are removed automatically.</footer>
</main>
<script>
const q=document.getElementById('q'),r=document.getElementById('region'),t=document.getElementById('topic');
const evs=[...document.querySelectorAll('.ev')],empty=document.getElementById('empty');
function f(){const s=q.value.trim().toLowerCase();let n=0;
evs.forEach(e=>{const ok=(!s||e.dataset.search.includes(s))&&(!r.value||e.dataset.region===r.value)&&(!t.value||e.dataset.topics.split(' ').includes(t.value));e.hidden=!ok;if(ok)n++});
empty.hidden=n>0}
[q,r,t].forEach(x=>x.addEventListener('input',f));
</script></body></html>"""


def main():
    items = load()

    def opts(d):
        return "".join(f'<option value="{k}">{v}</option>' for k, v in d.items())

    page = (PAGE.replace("__REGIONS__", opts(REGIONS)).replace("__TOPICS__", opts(TOPICS))
            .replace("__ROWS__", "\n".join(row(c) for c in items))
            .replace("__COUNT__", str(len(items)))
            .replace("__TODAY__", f"{dt.date.today():%d %b %Y}"))
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"Built {len(items)} events")


if __name__ == "__main__":
    main()
