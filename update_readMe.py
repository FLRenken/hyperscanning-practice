
import json
import re
from pathlib import Path

README = Path("README.md")
RESULTS = Path("results.json")

results = json.loads(RESULTS.read_text(encoding="utf-8"))

# --------------------------------------------------
# 1. PLV results
# --------------------------------------------------

conditions = results["notebook_1"]["conditions"]

lines = [
    "| Condition | Real pairs | Shuffled pairs | p-value |",
    "|---|---:|---:|---:|",
]

for name, values in conditions.items():
    fmt = lambda x: f"{x:.4f}" if x is not None else "N/A"

    lines.append(
        f"| {name} | {fmt(values.get('real'))} "
        f"| {fmt(values.get('shuffled'))} "
        f"| {fmt(values.get('p'))} |"
    )

plv_table = "\n".join(lines)

# --------------------------------------------------
# 2. Preprocessing results
# --------------------------------------------------

preprocessing = results.get("preprocessing", {})

lines = [
    "| Subject | Boundary | Practice | Real | Complete | Duet | Constant pitch |",
    "|---|---|---:|---:|---:|---:|---:|",
]

for sub, values in sorted(preprocessing.items()):
    lines.append(
        f"| {sub} "
        f"| {values.get('boundary', 'N/A')} "
        f"| {values.get('practice', 'N/A')} "
        f"| {values.get('real', 'N/A')} "
        f"| {values.get('complete', 'N/A')} "
        f"| {values.get('duet', 'N/A')} "
        f"| {values.get('constant_pitch', 'N/A')} |"
    )

preprocessing_table = "\n".join(lines)

# --------------------------------------------------
# 3. Replace README sections
# --------------------------------------------------

readme = README.read_text(encoding="utf-8")

def replace_section(readme, start_marker, end_marker, table):
    pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)

    replacement = (
        start_marker + "\n"
        + table + "\n"
        + end_marker
    )

    updated, count = re.subn(
        pattern,
        lambda _: replacement,
        readme,
        count=1,
        flags=re.DOTALL
    )

    if count == 0:
        raise ValueError(f"Could not find markers: {start_marker}")

    return updated


readme = replace_section(
    readme,
    "<!-- PLV_RESULTS_START -->",
    "<!-- PLV_RESULTS_END -->",
    plv_table
)

''' readme = replace_section(
    readme,
    "<!-- PREPROCESSING_RESULTS_START -->",
    "<!-- PREPROCESSING_RESULTS_END -->",
    preprocessing_table
) '''

README.write_text(readme, encoding="utf-8")

print("README.md updated successfully.")
