
import json
import re
from pathlib import Path

README = Path("README.md")
RESULTS = Path("results.json")

# Load results
with RESULTS.open("r", encoding="utf-8") as f:
    results = json.load(f)

conditions = results["notebook_1"]["conditions"]

# Build Markdown table
lines = [
    "| Condition | Real pairs | Shuffled pairs | p-value |",
    "|---|---:|---:|---:|",
]

for name, values in conditions.items():
    real = values.get("real")
    shuffled = values.get("shuffled")
    p_value = values.get("p")

    fmt = lambda x: f"{x:.4f}" if x is not None else "N/A"

    lines.append(
        f"| {name} | {fmt(real)} | {fmt(shuffled)} | {fmt(p_value)} |"
    )

table = "\n".join(lines)

# Replace only the content between the markers
readme = README.read_text(encoding="utf-8")

pattern = r"<!-- PLV_RESULTS_START -->.*?<!-- PLV_RESULTS_END -->"
replacement = (
    "<!-- PLV_RESULTS_START -->\n"
    + table
    + "\n<!-- PLV_RESULTS_END -->"
)

updated, count = re.subn(
    pattern, lambda _: replacement, readme, count=1, flags=re.DOTALL
)

if count == 0:
    raise ValueError("Could not find PLV result markers in README.md")

README.write_text(updated, encoding="utf-8")
print("README.md updated successfully.")
