"""The look of the site, after the presentation page (amoorion-website) and resources/: night, rose and gold."""

FONTS = (
    "https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Cormorant+Garamond:wght@500;700"
    "&family=Plus+Jakarta+Sans:wght@400;600&display=swap"
)
STYLE = """
:root { --bg: #07090e; --fg: #f2e9e4; --muted: #b9a9a3; --line: rgba(226, 168, 147, 0.22);
  --rose: #e14c62; --gold: #e2a893; --card: #0d101a; }
* { box-sizing: border-box; }
body { margin: 0; background: radial-gradient(ellipse at top, #1a0f18 0%, var(--bg) 55%) fixed; color: var(--fg);
  font: 16px/1.65 "Plus Jakarta Sans", system-ui, -apple-system, sans-serif; }
main, header, footer { max-width: 56rem; margin: 0 auto; padding: 0 1rem; }
header { padding-top: 2.2rem; padding-bottom: 1.4rem; border-bottom: 1px solid var(--line); text-align: center; }
header img { max-width: min(30rem, 90%); height: auto; }
header p { color: var(--muted); margin: 0.3rem 0 1rem; }
h1, h2, h3 { font-family: "Cormorant Garamond", Georgia, serif; color: var(--gold); line-height: 1.2; }
h2 { font-size: 2rem; margin-top: 2.4rem; }
nav a { margin: 0 0.6rem; color: var(--gold); text-decoration: none; font-family: Cinzel, serif;
  font-size: 0.9rem; letter-spacing: 0.08em; }
nav a:hover { color: var(--rose); }
.version { display: inline-block; padding: 0.1rem 0.7rem; border: 1px solid var(--line); border-radius: 999px;
  font-size: 0.85rem; color: var(--gold); }
pre, code { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.9em; }
pre { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 0.9rem; overflow-x: auto; }
a { color: var(--rose); }
table { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
th, td { border-bottom: 1px solid var(--line); padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.9rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem;
  text-decoration: none; color: inherit; transition: border-color 0.2s, box-shadow 0.2s; }
.card:hover { border-color: rgba(225, 76, 98, 0.6); box-shadow: 0 0 20px rgba(225, 76, 98, 0.2); }
.card h3 { margin: 0 0 0.3rem; font-size: 1.3rem; }
.card p { margin: 0; color: var(--muted); font-size: 0.92rem; }
footer { color: var(--muted); font-size: 0.85rem; padding-top: 2rem; padding-bottom: 3rem;
  border-top: 1px solid var(--line); margin-top: 3rem; text-align: center; }
"""
