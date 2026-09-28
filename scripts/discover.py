"""Ask Claude (with web search) for new conferences and append them to data/conferences.yml.

Run by the monthly workflow, which opens a pull request so you can review before publishing.
Needs the ANTHROPIC_API_KEY environment variable.
"""
import datetime as dt
import json
import os
import pathlib
import re
import sys

import anthropic
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "conferences.yml"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

PROMPT = """Today is {today}. Use web search to find conferences, symposia, workshops, summer schools
and hackathons starting between {today} and {horizon} on: Earth observation and remote sensing,
methane, greenhouse gases, emissions monitoring, and machine learning / deep learning / AI applied to
these (or to Earth science generally). Prioritise Europe, but include major events worldwide.

Search these organisations' event pages specifically, one at a time:
WMO (World Meteorological Organization), ICOS (Integrated Carbon Observation System),
ESA (for example the Living Planet Symposium, Phi-Week, EO Open Science, ESA training courses),
ECMWF, EUMETSAT, and ESA PhiLab / Phi-Lab. Also search generally for EO and climate hackathons.

Set "type" to "hackathon" for hackathons, challenges and datathons, otherwise "conference".
For every event look for the abstract submission deadline (registration or application deadline for
hackathons) and include it if published, otherwise null.

Already listed (do not repeat): {known}

Only include events whose official page you actually found, with confirmed dates. Do not guess.
Reply with ONLY a JSON array (no prose, no code fences). Each item:
{{"name": str, "type": "conference" or "hackathon", "start": "YYYY-MM-DD", "end": "YYYY-MM-DD",
"city": str, "country": str, "region": "europe" or "world",
"topics": subset of ["eo","methane","ghg","emissions","ai"],
"url": official page, "deadline": "YYYY-MM-DD" or null}}"""


def ask(prompt):
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": prompt}]
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 30}]
    for _ in range(6):  # continue if the server pauses a long search turn
        resp = client.messages.create(model=MODEL, max_tokens=8000, tools=tools, messages=messages)
        if resp.stop_reason != "pause_turn":
            return "".join(b.text for b in resp.content if b.type == "text")
        messages = [messages[0], {"role": "assistant", "content": resp.content}]
    return ""


def main():
    existing = yaml.safe_load(DATA.read_text(encoding="utf-8")) or []
    known_urls = {c["url"].rstrip("/") for c in existing}
    known_names = {c["name"].lower() for c in existing}
    today = dt.date.today()
    horizon = today + dt.timedelta(days=548)
    text = ask(PROMPT.format(today=today, horizon=horizon,
                             known="; ".join(sorted(known_names)) or "none"))
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        print("No JSON in reply; nothing added.")
        return
    added = 0
    for c in json.loads(match.group(0)):
        try:
            if c["url"].rstrip("/") in known_urls or c["name"].lower() in known_names:
                continue
            entry = {
                "name": c["name"], "start": dt.date.fromisoformat(c["start"]),
                "end": dt.date.fromisoformat(c.get("end") or c["start"]),
                "city": c.get("city", ""), "country": c.get("country", ""),
                "region": c.get("region", "world"),
                "topics": [t for t in c.get("topics", []) if t in {"eo", "methane", "ghg", "emissions", "ai"}],
                "url": c["url"],
            }
            if c.get("type") == "hackathon":
                entry["type"] = "hackathon"
            if c.get("deadline"):
                entry["deadline"] = c["deadline"]
            existing.append(entry)
            added += 1
        except (KeyError, ValueError) as exc:
            print(f"Skipped malformed item: {exc}", file=sys.stderr)
    existing.sort(key=lambda c: str(c["start"]))
    DATA.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Added {added} candidate events")


if __name__ == "__main__":
    main()
