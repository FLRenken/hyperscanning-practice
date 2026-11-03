"""
Write the analysis results from results.json into README.md.

Each measure has its own pair of markers in the README:

    <!-- NB2_ONE_SAMPLE_START -->
    (table + auto-summary are written here by this script)
    <!-- NB2_ONE_SAMPLE_END -->

    **Interpretation.** Hand-written text below the END marker is never touched.

Adding a new measure:
    1. Write a builder function `build_xyz(results) -> str`.
    2. Add `("XYZ", build_xyz)` to MEASURES at the bottom.
    3. Add `<!-- XYZ_START -->` / `<!-- XYZ_END -->` to the README,
       with an interpretation paragraph underneath.
Measures whose markers are missing from the README are skipped with a warning,
and measures whose data is missing from results.json are skipped as well.
"""

import argparse
import json
import re
from pathlib import Path

ALPHA = 0.05

CONDITION_NAMES = {
    "duet": "Duet",
    "constant_pitch": "Constant pitch",
}

MEASURE_NAMES = {
    "real_PLV": "Real PLV",
    "shuffled_PLV": "Shuffled PLV",
    "excess_PLV": "Excess PLV (real − shuffled)",
}


# --------------------------------------------------
# Formatting helpers
# --------------------------------------------------

def fmt(x, digits=4):
    if x is None:
        return "N/A"
    if isinstance(x, int):
        return str(x)
    return f"{x:.{digits}f}"


def p_fmt(p):
    if p is None:
        return "N/A"
    return "< .001" if p < 0.001 else f"{p:.3f}"


def ci_fmt(ci, digits=4):
    if ci is None:
        return "N/A"
    return f"[{fmt(ci[0], digits)}, {fmt(ci[1], digits)}]"


def cond(name):
    return CONDITION_NAMES.get(name, name)


def measure(name):
    return MEASURE_NAMES.get(name, name)


def ci_includes_zero(ci):
    return ci is not None and ci[0] <= 0 <= ci[1]


def sig_word(p):
    return "significant" if p is not None and p < ALPHA else "not significant"


def effect_label(d):
    """Cohen's (1988) conventional thresholds."""
    if d is None:
        return "unknown"
    d = abs(d)
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


def auto_summary(sentences):
    return "\n\n" + f"> **Auto-summary:** {' '.join(sentences)}"


# --------------------------------------------------
# Notebook 1 (proof of concept, 1 dyad)
# --------------------------------------------------

def build_nb1_plv(results):
    conditions = results["notebook_1"]["conditions"]
    lines = [
        "| Condition | Real pairs | Shuffled pairs | p-value |",
        "|---|---:|---:|---:|",
    ]
    for name, v in conditions.items():
        lines.append(
            f"| {cond(name)} | {fmt(v.get('real'))} "
            f"| {fmt(v.get('shuffled'))} | {p_fmt(v.get('p'))} |"
        )
    return "\n".join(lines)


# --------------------------------------------------
# Notebook 2 builders (one per measure)
# --------------------------------------------------

def build_nb2_descriptive(results):
    n2 = results["notebook_2"]
    desc = n2["descriptive_statistics"]

    lines = [
        f"*Status: {n2.get('status', 'N/A')} · metric: {n2.get('metric', 'N/A')} · "
        f"unit of analysis: {n2.get('unit_of_analysis', 'N/A')} · "
        f"N = {n2.get('n_dyads', 'N/A')} dyads*",
        "",
        "| Condition | Measure | N | Mean | SD | SEM | 95% CI |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for c, measures in desc.items():
        for m, v in measures.items():
            lines.append(
                f"| {cond(c)} | {measure(m)} | {v['n']} | {fmt(v['mean'])} "
                f"| {fmt(v['sd'])} | {fmt(v.get('sem'))} | {ci_fmt(v.get('ci_95'))} |"
            )

    sentences = []
    for c, measures in desc.items():
        ex = measures.get("excess_PLV")
        if ex is None:
            continue
        zero = "includes" if ci_includes_zero(ex.get("ci_95")) else "excludes"
        sentences.append(
            f"{cond(c)}: mean excess PLV = {fmt(ex['mean'])}, "
            f"95% CI {ci_fmt(ex.get('ci_95'))} ({zero} zero)."
        )
    return "\n".join(lines) + auto_summary(sentences)


def build_nb2_one_sample(results):
    n2 = results["notebook_2"]
    tests = n2["one_sample_excess_PLV_vs_zero"]
    desc = n2["descriptive_statistics"]

    lines = [
        "| Condition | Mean excess PLV | t | df | p | Cohen's d | Wilcoxon W | Wilcoxon p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    sentences = []
    for c, v in tests.items():
        mean = desc.get(c, {}).get("excess_PLV", {}).get("mean")
        lines.append(
            f"| {cond(c)} | {fmt(mean)} | {fmt(v['t'], 2)} | {v['df']} "
            f"| {p_fmt(v['p_value'])} | {fmt(v['cohens_d'], 2)} "
            f"| {fmt(v.get('wilcoxon_statistic'), 1)} | {p_fmt(v.get('wilcoxon_p'))} |"
        )
        sentences.append(
            f"{cond(c)}: t({v['df']}) = {fmt(v['t'], 2)}, p = {p_fmt(v['p_value'])} "
            f"({sig_word(v['p_value'])}), d = {fmt(v['cohens_d'], 2)} "
            f"({effect_label(v['cohens_d'])})."
        )
    return "\n".join(lines) + auto_summary(sentences)


def paired_block(data, label):
    lines = [
        "| Mean difference | 95% CI | t | df | p | Cohen's dz | Wilcoxon W | Wilcoxon p |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| {fmt(data['mean_difference'])} | {ci_fmt(data['ci_95'])} "
            f"| {fmt(data['t'], 2)} | {data['df']} | {p_fmt(data['p_value'])} "
            f"| {fmt(data['cohens_dz'], 2)} | {fmt(data.get('wilcoxon_statistic'), 1)} "
            f"| {p_fmt(data.get('wilcoxon_p'))} |"
        ),
    ]
    zero = "includes" if ci_includes_zero(data["ci_95"]) else "excludes"
    sentences = [
        f"{label} (duet − constant pitch): Δ = {fmt(data['mean_difference'])}, "
        f"95% CI {ci_fmt(data['ci_95'])} ({zero} zero), "
        f"t({data['df']}) = {fmt(data['t'], 2)}, p = {p_fmt(data['p_value'])} "
        f"({sig_word(data['p_value'])}), dz = {fmt(data['cohens_dz'], 2)} "
        f"({effect_label(data['cohens_dz'])})."
    ]
    return "\n".join(lines) + auto_summary(sentences)


def build_nb2_paired_excess(results):
    return paired_block(
        results["notebook_2"]["paired_excess_PLV_duet_vs_constant_pitch"], "Excess PLV"
    )


def build_nb2_paired_real(results):
    return paired_block(
        results["notebook_2"]["paired_real_PLV_duet_vs_constant_pitch"], "Real PLV"
    )


# --------------------------------------------------
# README replacement
# --------------------------------------------------

def replace_section(readme, key, content):
    start, end = f"<!-- {key}_START -->", f"<!-- {key}_END -->"
    pattern = re.escape(start) + r".*?" + re.escape(end)
    replacement = f"{start}\n\n{content}\n\n{end}"
    return re.subn(pattern, lambda _: replacement, readme, count=1, flags=re.DOTALL)


# Registry: (marker key, builder). Add new measures here.
MEASURES = [
    ("PLV_RESULTS", build_nb1_plv),
    ("NB2_DESCRIPTIVE", build_nb2_descriptive),
    ("NB2_ONE_SAMPLE", build_nb2_one_sample),
    ("NB2_PAIRED_EXCESS", build_nb2_paired_excess),
    ("NB2_PAIRED_REAL", build_nb2_paired_real),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--readme", default="README.md", type=Path)
    parser.add_argument("--results", default="results.json", type=Path)
    args = parser.parse_args()

    results = json.loads(args.results.read_text(encoding="utf-8"))
    readme = args.readme.read_text(encoding="utf-8")

    for key, builder in MEASURES:
        try:
            content = builder(results)
        except (KeyError, TypeError) as e:
            print(f"skipped {key}: data missing in {args.results} ({e})")
            continue
        readme, count = replace_section(readme, key, content)
        print(f"{'updated' if count else 'skipped'} {key}"
              + ("" if count else f": markers not found in {args.readme}"))

    args.readme.write_text(readme, encoding="utf-8")
    print(f"{args.readme} written.")


if __name__ == "__main__":
    main()