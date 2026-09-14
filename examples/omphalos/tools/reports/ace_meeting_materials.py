"""Build the personal brief and advisor deck from audited report exports.

Both harnesses: python -m tools.reports.ace_meeting_materials
Only local report data and explicitly selected code excerpts are read.
No benchmark loader, experiment runner, model client, or Rocq is invoked.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report/ace_retrospective"
BUILD = OUT / ".build/meeting"
FIGURES = OUT / "meeting_figures"
NAVY = "173247"
TEAL = "087F8C"
ORANGE = "D67B32"
MUTED = "687C8D"
COLORS = {"none": "#687C8D", "luna": "#087F8C", "terra": "#D67B32"}
INPUTS: dict[str, str] = {}
CHECKS: list[dict[str, Any]] = []
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(name: str) -> list[dict[str, str]]:
    # Deliberately no user path/glob input or imports of historical runners.
    if name not in {
        "crossover",
        "cumulative_curves",
        "budget_history",
        "archive_summary",
        "continuations",
        "amortization",
        "preparation",
    }:
        raise ValueError(f"Unregistered report table: {name}")
    path = OUT / "data" / f"{name}.csv"
    INPUTS[path.relative_to(ROOT).as_posix()] = digest(path)
    with path.open() as stream:
        return list(csv.DictReader(stream))


def close(label: str, actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, abs_tol=1e-6, rel_tol=1e-6):
        raise ValueError(f"{label}: {actual} != {expected}")
    CHECKS.append(dict(check=label, actual=actual, expected=expected))


def charts() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(BUILD / "matplotlib"))
    mpl: Any = importlib.import_module("matplotlib")
    mpl.use("Agg")
    plt: Any = importlib.import_module("matplotlib.pyplot")
    patches: Any = importlib.import_module("matplotlib.patches")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 15,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#173247",
            "text.color": "#173247",
            "xtick.color": "#526775",
            "ytick.color": "#526775",
            "axes.edgecolor": "#B6C4CD",
            "axes.titleweight": "bold",
            "pdf.fonttype": 42,
        }
    )

    def save(name: str, fig: Any) -> None:
        for suffix in ("png", "pdf"):
            fig.savefig(
                FIGURES / f"{name}.{suffix}",
                dpi=180,
                bbox_inches="tight",
                facecolor="white",
            )
        plt.close(fig)

    cross = {r["arm"]: r for r in table("crossover")}
    luna = cross["gpt-5.6-luna/luna"]
    none = cross["gpt-5.6-luna/none"]
    for arm, solves in {
        "gpt-5.6-luna/none": 24,
        "gpt-5.6-luna/luna": 27,
        "gpt-5.6-luna/terra": 24,
        "gpt-5.6-terra/none": 29,
        "gpt-5.6-terra/luna": 29,
        "gpt-5.6-terra/terra": 30,
    }.items():
        close(arm + " cells", float(cross[arm]["cells"]), 40)
        close(arm + " solves", float(cross[arm]["qualified_solves"]), solves)
    close("Luna own-book bill", float(luna["cost"]), 0.66722836)
    close("Luna no-book bill", float(none["cost"]), 0.77651210)
    close(
        "Luna uncached difference percent (rounded)",
        round(
            100
            * (
                float(luna["uncached_cost"]) / float(none["uncached_cost"]) - 1
            ),
            2,
        ),
        1.45,
    )

    fig, ax = plt.subplots(figsize=(8, 3.1))
    ax.set(xlim=(-0.15, 10.1), ylim=(-0.05, 4))
    ax.axis("off")
    boxes = [
        (0, 2.4, "Generator", "Proof attempt"),
        (3.6, 2.4, "Rocq", "Checked evidence"),
        (7.2, 2.4, "Reflector", "Lessons"),
        (7.2, 0.1, "Curator /\nReducer", "Proposed changes"),
        (3.6, 0.1, "Merge + book", "Deterministic code"),
    ]
    for x, y, title, subtitle in boxes:
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, y),
                2.7,
                1.4,
                boxstyle="round,pad=0.05",
                facecolor="#EAF4F4",
                edgecolor="#087F8C",
                linewidth=1.4,
            )
        )
        ax.text(
            x + 1.35,
            y + 0.9,
            title,
            ha="center",
            va="center",
            fontsize=16,
            weight="bold",
        )
        ax.text(x + 1.35, y + 0.24, subtitle, ha="center", fontsize=11)
    for start, end in [
        ((2.75, 3.1), (3.5, 3.1)),
        ((6.35, 3.1), (7.1, 3.1)),
        ((8.55, 2.3), (8.55, 1.55)),
        ((7.1, 0.8), (6.4, 0.8)),
        ((3.5, 0.8), (1.35, 2.3)),
    ]:
        ax.annotate(
            "",
            end,
            start,
            arrowprops=dict(arrowstyle="->", lw=2, color="#687C8D"),
        )
    ax.text(
        1.25,
        0.45,
        "Persistent advice\nfor later attempts",
        ha="center",
        fontsize=12,
    )
    save("pipeline", fig)

    bounded = [
        r
        for r in table("budget_history")
        if r["campaign"] == "ace_bounded_20260908"
    ]
    close(
        "Bounded saving percent (rounded)",
        round(
            100 * (1 - float(bounded[1]["cost"]) / float(bounded[0]["cost"])),
            1,
        ),
        55.5,
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.7, 4.1), layout="constrained")
    for ax, key, title, upper in zip(
        axes,
        ("cost", "solves"),
        ("Whole-panel dollars", "Solves / 40"),
        (1.8, 40),
    ):
        vals = [float(r[key]) for r in bounded]
        ax.bar([0, 1], vals, color=[COLORS["none"], COLORS["luna"]], width=0.6)
        ax.set_xticks([0, 1], ["Older X3", "Bounded"], fontsize=13)
        ax.set_ylim(0, upper)
        ax.set_title(title, fontsize=15)
        for i, v in enumerate(vals):
            ax.text(
                i,
                v + upper * 0.025,
                f"${v:.4f}" if key == "cost" else str(int(v)),
                ha="center",
                weight="bold",
                fontsize=16,
            )
    save("bounded", fig)

    old = next(
        r
        for r in table("archive_summary")
        if r["archive"] == "x_validation_agentic" and r["seed"] == "0"
    )
    close("Earlier validation solves", float(old["raw_solves"]), 27)
    fig, ax = plt.subplots(figsize=(7.7, 4.2), layout="constrained")
    vals = [int(old["raw_solves"]), 24, 27]
    bills = [float(old["cost_usd"]), float(none["cost"]), float(luna["cost"])]
    ax.barh(
        [2, 1, 0],
        vals,
        color=["#8996A3", COLORS["none"], COLORS["luna"]],
        height=0.58,
    )
    ax.set_yticks(
        [2, 1, 0],
        ["Earlier\nno book", "Current\nno book", "Current\nLuna book"],
    )
    ax.set(xlim=(0, 40), xlabel="Validation solves / 40")
    for y, v, bill in zip([2, 1, 0], vals, bills):
        ax.text(v + 0.6, y, f"{v}  |  ${bill:.4f}", va="center", fontsize=14)
    save("lineage", fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.5), layout="constrained")
    for j, book in enumerate(("none", "luna", "terra")):
        for i, model in enumerate(("luna", "terra")):
            count = int(cross[f"gpt-5.6-{model}/{book}"]["qualified_solves"])
            ax.add_patch(
                patches.Rectangle(
                    (j - 0.47, i - 0.4),
                    0.94,
                    0.8,
                    facecolor="#EAF4F4" if model == "luna" else "#FAEDDF",
                )
            )
            ax.text(
                j,
                i,
                str(count),
                ha="center",
                va="center",
                fontsize=36,
                weight="bold",
            )
    ax.set_xticks(
        [0, 1, 2], ["No book", "Luna book", "Terra book"], fontsize=16
    )
    ax.set_yticks([0, 1], ["Luna", "Terra"], fontsize=17)
    ax.set(
        xlim=(-0.55, 2.55),
        ylim=(1.55, -0.55),
        xlabel="Context supplied to solver",
    )
    ax.set_title("Qualified validation solves / 40", fontsize=18, pad=22)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    save("crossover", fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.2), layout="constrained")
    ax.annotate(
        "",
        (float(luna["cost"]), 27),
        (float(none["cost"]), 24),
        arrowprops=dict(arrowstyle="->", color="#A7BCC5", lw=2),
    )
    for row, label, color, off in [
        (none, "No book", COLORS["none"], (10, -25)),
        (luna, "Own book", COLORS["luna"], (10, 10)),
    ]:
        x, y = float(row["cost"]), int(row["qualified_solves"])
        ax.scatter([x], [y], s=180, color=color, zorder=4)
        ax.annotate(
            f"{label}\n{y}/40 · ${x:.4f}",
            (x, y),
            xytext=off,
            textcoords="offset points",
            fontsize=16,
            color=color,
        )
    ax.set(
        xlim=(0.60, 0.94),
        ylim=(22, 30),
        xlabel="Total panel spending ($)",
        ylabel="Qualified solves / 40",
    )
    ax.grid(alpha=0.16)
    save("matched", fig)

    curves = table("cumulative_curves")
    fig, axes = plt.subplots(
        1, 2, figsize=(8, 4.6), layout="constrained", sharey=True
    )
    for ax, model in zip(axes, ("luna", "terra")):
        for book, label in [
            ("none", "No book"),
            ("luna", "Luna book"),
            ("terra", "Terra book"),
        ]:
            points = [
                r
                for r in curves
                if r["model"] == f"gpt-5.6-{model}" and r["book"] == book
            ]
            assert len(points) == 41
            close(
                model + book + " curve cost",
                float(points[-1]["spend"]),
                float(cross[f"gpt-5.6-{model}/{book}"]["cost"]),
            )
            close(
                model + book + " curve solves",
                float(points[-1]["solves"]),
                float(cross[f"gpt-5.6-{model}/{book}"]["qualified_solves"]),
            )
            ax.step(
                [float(r["spend"]) for r in points],
                [int(r["solves"]) for r in points],
                where="post",
                lw=2.5,
                color=COLORS[book],
                label=label,
            )
        ax.set(title=model.title(), xlabel="Recorded dollars", ylim=(0, 40))
        ax.grid(alpha=0.18)
        ax.tick_params(labelsize=13)
    axes[0].set_ylabel("Qualified solves / 40", fontsize=14)
    axes[1].legend(loc="lower right", fontsize=11)
    save("spend", fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.7, 4.1), layout="constrained")
    for ax, key, title in zip(
        axes,
        ("cost", "uncached_cost"),
        ("Recorded bill", "All input uncached"),
    ):
        vals = [float(none[key]), float(luna[key])]
        ax.bar([0, 1], vals, color=[COLORS["none"], COLORS["luna"]], width=0.6)
        ax.set_xticks([0, 1], ["No book", "Own book"], fontsize=13)
        ax.set_ylim(0, max(vals) * 1.24)
        ax.set_title(title, fontsize=15)
        for i, v in enumerate(vals):
            ax.text(
                i,
                v + max(vals) * 0.045,
                f"${v:.4f}",
                ha="center",
                fontsize=14,
                weight="bold",
            )
    save("cache", fig)

    cont = table("continuations")
    fig, axes = plt.subplots(
        1, 2, figsize=(8, 4.4), layout="constrained", sharey=True
    )
    for ax, model in zip(axes, ("luna", "terra")):
        for context, label, color, marker in [
            ("C", "No ACE", COLORS["none"], "o"),
            ("E", "Corrected book", COLORS["luna"], "s"),
        ]:
            points = sorted(
                [r for r in cont if r["arm"] == f"gpt-5.6-{model}/{context}"],
                key=lambda r: int(r["level"]),
            )
            assert len(points) == 3
            ys = [int(r["qualified_solves"]) for r in points]
            expected = {
                "lunaC": [4, 4, 4],
                "lunaE": [3, 3, 3],
                "terraC": [4, 6, 6],
                "terraE": [3, 7, 7],
            }[model + context]
            assert ys == expected
            CHECKS.append(
                dict(
                    check=model + context + " continuation sequence",
                    actual=ys,
                    expected=expected,
                )
            )
            ax.plot(
                [0, 1, 2], ys, marker=marker, lw=2.5, color=color, label=label
            )
        ax.set(title=model.title(), ylim=(0, 8), yticks=[0, 2, 4, 6, 8])
        ax.set_xticks(
            [0, 1, 2], ["Initial", "More\nmoney", "More\nlimits"], fontsize=12
        )
        ax.grid(alpha=0.18)
    axes[0].set_ylabel("Solves / 8 selected problems", fontsize=13)
    axes[1].legend(loc="lower right", fontsize=11)
    save("continuations", fig)

    amort = table("amortization")
    prep = table("preparation")
    fig, axes = plt.subplots(1, 2, figsize=(8, 4.3), layout="constrained")
    for ax, model in zip(axes, ("luna", "terra")):
        points = [r for r in amort if r["model"] == model]
        cost = sum(float(r["cost"]) for r in prep if r["model"] == model)
        close(
            model + " preparation",
            cost,
            0.91692376 if model == "luna" else 8.0992186,
        )
        ax.plot(
            [int(r["problems"]) for r in points],
            [float(r["amortized_per_problem"]) for r in points],
            marker="o",
            lw=2,
            color=COLORS[model],
            label="Own book + preparation / N",
        )
        ax.axhline(
            float(points[0]["no_book_inference_per_problem"]),
            ls="--",
            color=COLORS["none"],
            label="No book",
        )
        ax.set(
            xscale="log",
            title=model.title(),
            xlabel="Future tasks (log scale)",
        )
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("Dollars per attempted task", fontsize=13)
    axes[0].legend(loc="upper right", fontsize=9)
    save("preparation", fig)


@dataclass(frozen=True)
class Slide:
    title: str
    bullets: list[str]
    image: str | None
    takeaway: str
    notes: str


def slides() -> list[Slide]:
    text = (OUT / "advisor_slides.md").read_text()
    parts = re.split(r"^# ", text, flags=re.M)[1:]
    result: list[Slide] = []
    for part in parts:
        title, body = part.split("\n", 1)
        note = re.search(r"::: notes\n(.*?)\n:::", body, re.S)
        assert note is not None
        main = body[: note.start()]
        bullets = re.findall(r"^- (.+)$", main, re.M)
        assert 3 <= len(bullets) <= 4
        graphic = re.search(r"!\[[^]]*\]\(([^)]+)\)", main)
        takeaway = re.search(r"^> (.+)$", main, re.M)
        assert takeaway is not None
        result.append(
            Slide(
                title,
                bullets,
                graphic[1] if graphic else None,
                takeaway[1],
                note[1],
            )
        )
    assert len(result) == 16
    assert all(s.title.startswith("B") for s in result[12:])
    return result


def elem(parent: ET.Element, tag: str, **attrs: str) -> ET.Element:
    prefix, local = tag.split(":")
    return ET.SubElement(parent, f"{{{NS[prefix]}}}{local}", attrs)


def units(value: float) -> str:
    return str(round(value * 914400))


def text_box(
    tree: ET.Element,
    ident: int,
    x: float,
    y: float,
    w: float,
    h: float,
    paragraphs: list[str],
    size: float = 24,
    color: str = NAVY,
    bold: bool = False,
    bullets: bool = False,
    fill: str | None = None,
) -> None:
    sp = elem(tree, "p:sp")
    nv = elem(sp, "p:nvSpPr")
    elem(nv, "p:cNvPr", id=str(ident), name=f"Text {ident}")
    elem(nv, "p:cNvSpPr", txBox="1")
    elem(nv, "p:nvPr")
    props = elem(sp, "p:spPr")
    transform = elem(props, "a:xfrm")
    elem(transform, "a:off", x=units(x), y=units(y))
    elem(transform, "a:ext", cx=units(w), cy=units(h))
    elem(elem(props, "a:prstGeom", prst="rect"), "a:avLst")
    if fill:
        elem(elem(props, "a:solidFill"), "a:srgbClr", val=fill)
    else:
        elem(props, "a:noFill")
    elem(elem(props, "a:ln"), "a:noFill")
    body = elem(sp, "p:txBody")
    bp = elem(
        body, "a:bodyPr", wrap="square", lIns="0", rIns="0", tIns="0", bIns="0"
    )
    elem(bp, "a:noAutofit")
    elem(body, "a:lstStyle")
    for text in paragraphs:
        para = elem(body, "a:p")
        pp = elem(
            para,
            "a:pPr",
            marL="240000" if bullets else "0",
            indent="-240000" if bullets else "0",
        )
        elem(elem(pp, "a:lnSpc"), "a:spcPct", val="112000")
        elem(elem(pp, "a:spcAft"), "a:spcPts", val="1700" if bullets else "0")
        if bullets:
            elem(pp, "a:buFont", typeface="DejaVu Sans")
            elem(pp, "a:buChar", char="•")
        else:
            elem(pp, "a:buNone")
        run = elem(para, "a:r")
        rp = elem(
            run,
            "a:rPr",
            lang="en-US",
            sz=str(round(size * 100)),
            b="1" if bold else "0",
        )
        elem(elem(rp, "a:solidFill"), "a:srgbClr", val=color)
        elem(rp, "a:latin", typeface="DejaVu Sans")
        elem(run, "a:t").text = text


def picture(tree: ET.Element, rel: str, path: Path) -> None:
    width, height = struct.unpack(">II", path.read_bytes()[16:24])
    scale = min(7.55 / width, 4.65 / height)
    w, h = width * scale, height * scale
    x, y = 0.55 + (7.55 - w) / 2, 1.65 + (4.65 - h) / 2
    pic = elem(tree, "p:pic")
    nv = elem(pic, "p:nvPicPr")
    elem(nv, "p:cNvPr", id="20", name=path.stem)
    elem(elem(nv, "p:cNvPicPr"), "a:picLocks", noChangeAspect="1")
    elem(nv, "p:nvPr")
    bf = elem(pic, "p:blipFill")
    elem(bf, "a:blip", **{f"{{{NS['r']}}}embed": rel})
    elem(elem(bf, "a:stretch"), "a:fillRect")
    pr = elem(pic, "p:spPr")
    tr = elem(pr, "a:xfrm")
    elem(tr, "a:off", x=units(x), y=units(y))
    elem(tr, "a:ext", cx=units(w), cy=units(h))
    elem(elem(pr, "a:prstGeom", prst="rect"), "a:avLst")


def powerpoint(items: list[Slide], *, export_pdf: bool = True) -> None:
    raw = BUILD / "pandoc_slides.pptx"
    seed = BUILD / "slide_package.md"
    seed.write_text(
        "\n\n".join(
            f"# {item.title}\n\n"
            + (f"![]({OUT / item.image})" if item.image else "Placeholder.")
            + f"\n\n::: notes\n{item.notes}\n:::"
            for item in items
        )
        + "\n"
    )
    subprocess.run(
        [
            "pandoc",
            str(seed),
            "-f",
            "markdown-implicit_figures",
            "-t",
            "pptx",
            "--slide-level=1",
            "-o",
            str(raw),
        ],
        cwd=OUT,
        check=True,
    )
    with zipfile.ZipFile(raw) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    names = [n for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    assert len(names) == 16
    presentation = ET.fromstring(parts["ppt/presentation.xml"])
    dimensions = presentation.find("p:sldSz", NS)
    assert dimensions is not None
    dimensions.attrib.update(
        cx=units(13.333333), cy=units(7.5), type="screen16x9"
    )
    parts["ppt/presentation.xml"] = ET.tostring(
        presentation, encoding="utf-8", xml_declaration=True
    )
    for index, item in enumerate(items, 1):
        name = f"ppt/slides/slide{index}.xml"
        root = ET.fromstring(parts[name])
        common = root.find("p:cSld", NS)
        assert common is not None
        tree = common.find("p:spTree", NS)
        assert tree is not None
        rels = [
            b.attrib[f"{{{NS['r']}}}embed"]
            for b in tree.findall(".//a:blip", NS)
        ]
        for child in list(tree)[2:]:
            tree.remove(child)
        background = ET.Element(f"{{{NS['p']}}}bg")
        elem(
            elem(elem(background, "p:bgPr"), "a:solidFill"),
            "a:srgbClr",
            val="FFFFFF",
        )
        common.insert(0, background)
        text_box(
            tree,
            2,
            0.58,
            0.22,
            11,
            0.22,
            ["OMPHALOS  /  DEVELOPMENT RESULTS  /  12 SEPTEMBER 2026"],
            10,
            MUTED,
        )
        text_box(
            tree, 3, 0.58, 0.64, 12.15, 1.05, [item.title], 30, NAVY, True
        )
        if item.image:
            assert len(rels) == 1
            picture(tree, rels[0], OUT / item.image)
            text_box(
                tree, 4, 8.55, 1.9, 4.12, 4.55, item.bullets, 22, bullets=True
            )
        else:
            text_box(
                tree,
                4,
                0.83,
                2.02,
                11.55,
                4.27,
                item.bullets,
                27,
                bullets=True,
            )
        text_box(
            tree, 5, 0.58, 6.60, 12.16, 0.49, [item.takeaway], 15, TEAL, True
        )
        text_box(
            tree,
            6,
            0.58,
            7.17,
            9,
            0.2,
            ["Advisor discussion · 13 September 2026"],
            10,
            MUTED,
        )
        number = (
            f"{index:02d} / 12" if index <= 12 else f"BACKUP {index - 12} / 4"
        )
        text_box(tree, 7, 11.1, 7.17, 1.8, 0.2, [number], 10, MUTED)
        parts[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(
        OUT / "advisor_slides.pptx", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    if not export_pdf:
        return
    # Isolated profile: no interference with a user's open LibreOffice session.
    subprocess.run(
        [
            "libreoffice",
            f"-env:UserInstallation={(BUILD / 'lo-profile').as_uri()}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(OUT),
            str(OUT / "advisor_slides.pptx"),
        ],
        check=True,
        timeout=90,
    )
    if not (OUT / "advisor_slides.pdf").is_file():
        raise RuntimeError("LibreOffice did not create the presentation PDF")


def pdf(source: str, target: str) -> None:
    subprocess.run(
        [
            "pandoc",
            source,
            "--standalone",
            "--pdf-engine=xelatex",
            "--resource-path=.",
            "-V",
            "papersize=a4",
            "-V",
            "geometry:margin=20mm",
            "-V",
            "fontsize=11pt",
            "-V",
            "mainfont=DejaVu Serif",
            "-V",
            "sansfont=DejaVu Sans",
            "-V",
            "monofont=DejaVu Sans Mono",
            "-V",
            "colorlinks=true",
            "-o",
            target,
        ],
        cwd=OUT,
        check=True,
    )


def pages(path: Path) -> int:
    text = subprocess.check_output(["pdfinfo", str(path)], text=True)
    found = re.search(r"Pages:\s+(\d+)", text)
    assert found is not None
    return int(found[1])


def excerpts() -> None:
    selections = [
        ("prove_ace.py", 92, 112),
        ("prove_ace.py", 289, 309),
        ("runtime/campaign_budget.py", 262, 290),
    ]
    lines = [
        "# Prepared file excerpts",
        "",
        "Read-only excerpts for rehearsal; no model or Rocq calls.",
        "",
    ]
    for name, start, end in selections:
        path = ROOT / name
        INPUTS[name] = digest(path)
        content = path.read_text().splitlines()
        lines.extend(
            [
                f"## {name}:{start}",
                "",
                "```python",
                *content[start - 1 : end],
                "```",
                "",
            ]
        )
    path = OUT / "data/creator_terminal_evidence.json"
    INPUTS[path.relative_to(ROOT).as_posix()] = digest(path)
    rows = json.loads(path.read_text())
    witness = next(r for r in rows if r["theorem"] == "amc12_2000_p6")
    excerpt = {
        k: witness[k]
        for k in ("theorem", "final_tactic_visible", "last_tactic")
    }
    excerpt["final_check.category"] = witness["final_check"]["category"]
    excerpt["final_check.success"] = witness["final_check"]["success"]
    excerpt["verified_code_last_line"] = witness["verified_code"].splitlines()[
        -1
    ]
    lines.extend(
        [
            "## Terminal witness: first array entry",
            "",
            "```json",
            json.dumps(excerpt, indent=2),
            "```",
            "",
            "The `false` flag means the accepted terminal tactic was missing from the last submitted text. It is not a failed proof.",
            "",
        ]
    )
    (OUT / "rehearsal_excerpts.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader-only", action="store_true")
    parser.add_argument(
        "--defer-slide-pdf",
        action="store_true",
        help="Export PowerPoint separately when a sandbox blocks LibreOffice",
    )
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    old = json.loads((OUT / "verification.json").read_text())
    for name, expected in old["artifact_sha256"].items():
        if digest(OUT / name) != expected:
            raise ValueError(f"Original audited artifact changed: {name}")
    charts()
    excerpts()
    pdf("reader_brief.md", "reader_brief.pdf")
    count = pages(OUT / "reader_brief.pdf")
    print(f"Personal document: {count} pages", flush=True)
    if not args.reader_only:
        items = slides()
        powerpoint(items, export_pdf=not args.defer_slide_pdf)
        pdf("rehearsal_notes.md", "rehearsal_notes.pdf")
        if not args.defer_slide_pdf:
            assert pages(OUT / "advisor_slides.pdf") == 16
    assert 12 <= count <= 15, f"Expected 12–15 reading pages, got {count}"
    for name in (
        "report.md",
        "reader_brief.md",
        "advisor_slides.md",
        "rehearsal_notes.md",
        "next_session_prompt.md",
    ):
        path = OUT / name
        INPUTS[path.relative_to(ROOT).as_posix()] = digest(path)
    verification = {
        "edited": "2026-09-13",
        "evidence_snapshot": "2026-09-12",
        "reader_pages": count,
        "main_slides": 12,
        "backup_slides": 4,
        "numerical_checks": CHECKS,
        "input_sha256": INPUTS,
        "original_audited_artifacts_unchanged": True,
        "no_new_experiments": True,
        "no_benchmark_imports": True,
        "scope": "Derived from audited report exports and explicitly selected code excerpts; closed/mixed sources excluded.",
        "access_incident": "During September 13 planning, the mixed memory index was opened while checking standing guidance. It is excluded as an analytical input; the user reaffirmed testX closure. No protected outcome is used in these materials.",
        "visual_review": "Pending separate rendered-page review",
        "slide_pdf_export": "deferred"
        if args.defer_slide_pdf
        else "completed",
    }
    (OUT / "meeting_verification.json").write_text(
        json.dumps(verification, indent=2) + "\n"
    )
    print(
        f"Built meeting materials; {len(CHECKS)} numerical checks passed",
        flush=True,
    )


if __name__ == "__main__":
    main()
