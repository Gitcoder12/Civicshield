"""Extract the inline browser script so CI can syntax-check it with Node."""

import re
from pathlib import Path
from tempfile import gettempdir

html = Path("index.html").read_text(encoding="utf-8")
scripts = re.findall(r"<script\\b[^>]*>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL)
if len(scripts) != 1:
    raise SystemExit(f"Expected one inline application script, found {len(scripts)}")

output = Path(gettempdir()) / "civicshield-inline.js"
output.write_text(scripts[0], encoding="utf-8")
print(f"Extracted inline JavaScript to {output}")
