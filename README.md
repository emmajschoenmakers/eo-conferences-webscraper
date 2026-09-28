# Earth observation, methane & emissions conferences

A static site (GitHub Pages) listing upcoming conferences on Earth observation, methane, greenhouse
gases, emissions and ML/AI for these topics. Europe first, plus major events worldwide.

## How it works
- `data/conferences.yml` is the source of truth. Edit it to add or fix events.
- `scripts/build.py` turns it into `docs/index.html` and drops events that have finished.
- `pages.yml` rebuilds and deploys the site on every push and on the 2nd of each month.
- `discover.yml` (optional) runs on the 1st of each month, asks Claude with web search for new
  events and opens a pull request. You review and merge it; nothing goes live unchecked.

## Setup
1. Create a GitHub repo and push these files to `main`.
2. Settings > Pages > Source: **GitHub Actions**.
3. For automatic discovery: Settings > Secrets and variables > Actions > add `ANTHROPIC_API_KEY`
   (from console.anthropic.com), and Settings > Actions > General > enable
   **Allow GitHub Actions to create and approve pull requests**.
4. Run both workflows once from the Actions tab to test.

Without the API key the site still updates monthly; you just add events by hand.

## Entry format
```yaml
- name: Conference name
  start: 2027-04-04
  end: 2027-04-09
  city: Vienna
  country: Austria
  region: europe        # europe | world
  topics: [eo, methane, ghg, emissions, ai]
  url: https://example.org
  deadline: 2026-12-01  # optional
  note: Optional short note
```

## Local preview
`pip install pyyaml && python scripts/build.py`, then open `docs/index.html`.
