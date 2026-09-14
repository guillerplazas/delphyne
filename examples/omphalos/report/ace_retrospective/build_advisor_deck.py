"""Render only the advisor presentation; safe alongside runtime development.

Both harnesses: python report/ace_retrospective/build_advisor_deck.py
Uses explicit local development exports, Pandoc, Matplotlib and LibreOffice.
No Omphalos runtime imports, benchmark loading, experiments or network calls.
All writes stay in this presentation directory. Native PowerPoint text,
diagrams and table cells are editable; statistical charts are embedded PNGs.
"""

from __future__ import annotations

import argparse
import csv
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

import yaml
from PIL import ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BUILD = OUT / ".build/advisor_v2"
FIG = OUT / "advisor_figures"
W, H = 13.333333, 7.5
NAVY, TEAL, GOLD = "142C3B", "007E80", "D38B32"
INK, MUTED, BG, WHITE = "223D4A", "526A76", "F6F7F5", "FFFFFF"
PALE, LINE, RED = "E5F1EF", "DCE5E7", "AE4C44"
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)
INPUTS: dict[str, str] = {}
CHECKS: list[dict[str, Any]] = []
LAYOUT: list[dict[str, Any]] = []
OVERFLOWS: list[str] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remember(path: Path) -> Path:
    INPUTS[str(path.relative_to(ROOT))] = sha(path)
    return path


def rows(name: str) -> list[dict[str, str]]:
    if name not in {
        "crossover",
        "book_evolution",
        "preparation",
        "historical_matrix",
        "cumulative_curves",
        "continuations",
        "budget_history",
        "attribution",
    }:
        raise ValueError(name)
    with remember(OUT / "data" / f"{name}.csv").open() as stream:
        return list(csv.DictReader(stream))


def check(name: str, actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, abs_tol=1e-6, rel_tol=1e-6):
        raise ValueError(f"{name}: {actual} != {expected}")
    CHECKS.append(dict(name=name, actual=actual, expected=expected))


def clean(text: str) -> str:
    return text.replace("**", "").replace("\\n", "\n")


def e(parent: ET.Element, tag: str, **attrs: str) -> ET.Element:
    prefix, local = tag.split(":")
    return ET.SubElement(parent, f"{{{NS[prefix]}}}{local}", attrs)


def u(inches: float) -> str:
    return str(round(inches * 914400))


def font(size: float, bold: bool = False) -> Any:
    suffix = "-Bold" if bold else ""
    return ImageFont.truetype(
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{suffix}.ttf",
        round(size * 4),
    )


def line_count(text: str, size: float, width: float, bold: bool) -> int:
    face = font(size, bold)
    max_width = width * 72 * 4 * 0.95
    count = 0
    for explicit in clean(text).split("\n"):
        line = ""
        for token in explicit.split():
            candidate = f"{line} {token}".strip()
            if line and face.getlength(candidate) > max_width:
                count += 1
                line = token
            else:
                line = candidate
            # PowerPoint can wrap unusually long identifiers at characters.
            while face.getlength(line) > max_width:
                cut = max(1, int(len(line) * max_width / face.getlength(line)))
                count += 1
                line = line[cut:]
        count += 1
    return count


class Canvas:
    def __init__(self, tree: ET.Element, slide: int) -> None:
        self.tree, self.slide, self.ident = tree, slide, 1

    def shape(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        radius: bool = False,
        outline: str | None = None,
    ) -> ET.Element:
        self.ident += 1
        sp = e(self.tree, "p:sp")
        nv = e(sp, "p:nvSpPr")
        e(nv, "p:cNvPr", id=str(self.ident), name=f"Shape {self.ident}")
        e(nv, "p:cNvSpPr", txBox="1")
        e(nv, "p:nvPr")
        pr = e(sp, "p:spPr")
        tr = e(pr, "a:xfrm")
        e(tr, "a:off", x=u(x), y=u(y))
        e(tr, "a:ext", cx=u(w), cy=u(h))
        geom = e(pr, "a:prstGeom", prst="roundRect" if radius else "rect")
        av = e(geom, "a:avLst")
        if radius:
            e(av, "a:gd", name="adj", fmla="val 6500")
        if fill:
            e(e(pr, "a:solidFill"), "a:srgbClr", val=fill)
        else:
            e(pr, "a:noFill")
        ln = e(pr, "a:ln", w="7000")
        if outline:
            e(e(ln, "a:solidFill"), "a:srgbClr", val=outline)
        else:
            e(ln, "a:noFill")
        return sp

    def text(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        values: str | list[str],
        size: float = 20,
        color: str = INK,
        bold: bool = False,
        bullet: bool = False,
        align: str = "l",
        gap: float = 7,
        minimum: float | None = None,
    ) -> None:
        values = [values] if isinstance(values, str) else values
        minimum = minimum if minimum is not None else size
        requested = size
        while True:
            lines = sum(
                line_count(s, size, w - (0.20 if bullet else 0), bold)
                for s in values
            )
            height = (
                lines * size * (1.34 if bullet else 1.13) / 72
                + max(0, len(values) - 1) * gap / 72
            )
            if height <= h or size <= minimum:
                break
            size = max(minimum, size - 0.25)
        if height > h + 0.035:
            OVERFLOWS.append(
                f"Slide {self.slide}: text needs {height:.2f}in, has {h:.2f}in "
                f"at {size}pt: {values}"
            )
        LAYOUT.append(
            dict(
                slide=self.slide,
                text=[clean(t) for t in values],
                size=size,
                requested=requested,
                x=x,
                y=y,
                w=w,
                h=h,
            )
        )
        sp = self.shape(x, y, w, h, "")
        body = e(sp, "p:txBody")
        bp = e(
            body,
            "a:bodyPr",
            wrap="square",
            anchor="t",
            lIns="0",
            rIns="0",
            tIns="0",
            bIns="0",
        )
        e(bp, "a:noAutofit")
        e(body, "a:lstStyle")
        for value in values:
            para = e(body, "a:p")
            pp = e(
                para,
                "a:pPr",
                algn=align,
                marL=u(0.18) if bullet else "0",
                indent=u(-0.18) if bullet else "0",
            )
            e(e(pp, "a:lnSpc"), "a:spcPct", val="107000")
            e(e(pp, "a:spcAft"), "a:spcPts", val=str(round(gap * 100)))
            if bullet:
                e(pp, "a:buFont", typeface="DejaVu Sans")
                e(pp, "a:buChar", char="•")
            else:
                e(pp, "a:buNone")
            for i, segment in enumerate(
                value.replace("\\n", "\n").split("**")
            ):
                for j, chunk in enumerate(segment.split("\n")):
                    if j:
                        e(para, "a:br")
                    if not chunk:
                        continue
                    run = e(para, "a:r")
                    rp = e(
                        run,
                        "a:rPr",
                        lang="en-US",
                        sz=str(round(size * 100)),
                        b="1" if bold or i % 2 else "0",
                    )
                    e(e(rp, "a:solidFill"), "a:srgbClr", val=color)
                    e(rp, "a:latin", typeface="DejaVu Sans")
                    e(rp, "a:ea", typeface="DejaVu Sans")
                    e(run, "a:t").text = chunk
            e(para, "a:endParaRPr", lang="en-US", sz=str(round(size * 100)))

    def image(
        self, rel: str, path: Path, x: float, y: float, w: float, h: float
    ) -> None:
        pw, ph = struct.unpack(">II", path.read_bytes()[16:24])
        scale = min(w / pw, h / ph)
        iw, ih = pw * scale, ph * scale
        self.ident += 1
        pic = e(self.tree, "p:pic")
        nv = e(pic, "p:nvPicPr")
        e(
            nv,
            "p:cNvPr",
            id=str(self.ident),
            name=path.stem,
            descr="Observed data; standalone figure and source CSV provided",
        )
        e(e(nv, "p:cNvPicPr"), "a:picLocks", noChangeAspect="1")
        e(nv, "p:nvPr")
        bf = e(pic, "p:blipFill")
        e(bf, "a:blip", **{f"{{{NS['r']}}}embed": rel})
        e(e(bf, "a:stretch"), "a:fillRect")
        pr = e(pic, "p:spPr")
        tr = e(pr, "a:xfrm")
        e(tr, "a:off", x=u(x + (w - iw) / 2), y=u(y + (h - ih) / 2))
        e(tr, "a:ext", cx=u(iw), cy=u(ih))
        e(e(pr, "a:prstGeom", prst="rect"), "a:avLst")


def charts() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(BUILD / "matplotlib"))
    mpl: Any = importlib.import_module("matplotlib")
    mpl.use("Agg")
    plt: Any = importlib.import_module("matplotlib.pyplot")
    ticker: Any = importlib.import_module("matplotlib.ticker")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 16,
            "text.color": f"#{INK}",
            "axes.labelcolor": f"#{INK}",
            "xtick.color": f"#{MUTED}",
            "ytick.color": f"#{MUTED}",
            "axes.edgecolor": f"#{LINE}",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "axes.titleweight": "bold",
            "figure.facecolor": f"#{BG}",
            "axes.facecolor": f"#{BG}",
            "pdf.fonttype": 42,
        }
    )

    def save(fig: Any, name: str) -> None:
        for ext in ("png", "pdf"):
            fig.savefig(
                FIG / f"{name}.{ext}",
                dpi=190,
                bbox_inches="tight",
                facecolor=f"#{BG}",
            )
        plt.close(fig)

    cross = {r["arm"]: r for r in rows("crossover")}
    for model, counts in (("luna", (24, 27, 24)), ("terra", (29, 29, 30))):
        for book, solves in zip(("none", "luna", "terra"), counts):
            r = cross[f"gpt-5.6-{model}/{book}"]
            check(
                f"{model}/{book} solves", float(r["qualified_solves"]), solves
            )
            check(f"{model}/{book} cells", float(r["cells"]), 40)
            check(
                f"{model}/{book} cap",
                float(r["cap"]),
                0.1 if model == "luna" else 1,
            )
    b = [
        r
        for r in rows("budget_history")
        if r["campaign"] == "ace_bounded_20260908"
    ]
    b = {r["arm"]: r for r in b}
    check(
        "Bounded saves 55.5%",
        round(
            100
            * (
                1 - float(b["Bounded"]["cost"]) / float(b["Reference"]["cost"])
            ),
            1,
        ),
        55.5,
    )

    def pair(
        name: str, labels: list[str], solves: list[float], costs: list[float]
    ) -> None:
        fig, axes = plt.subplots(2, 1, figsize=(7.7, 4.6))
        fig.subplots_adjust(
            left=0.27, right=0.84, hspace=0.90, top=0.88, bottom=0.08
        )
        for ax, vals, title, money in zip(
            axes,
            (solves, costs),
            (
                "RECORDED TRAINING SOLVES / 40"
                if name == "training_gap"
                else "QUALIFIED SOLVES / 40",
                "WHOLE-PANEL DOLLARS",
            ),
            (False, True),
        ):
            ax.barh([1, 0], vals, color=[f"#{MUTED}", f"#{TEAL}"], height=0.55)
            ax.set_yticks([1, 0], labels, fontsize=15)
            ax.set_xlim(0, max(vals) * 1.22 if money else 42)
            ax.set_xticks([])
            ax.tick_params(axis="y", length=0)
            ax.set_title(title, loc="left", fontsize=13, pad=14)
            for y, val in zip([1, 0], vals):
                ax.text(
                    val + ax.get_xlim()[1] * 0.025,
                    y,
                    f"${val:.4f}" if money else f"{int(val)}/40",
                    va="center",
                    fontsize=18,
                    weight="bold",
                )
        save(fig, name)

    pair(
        "bounded",
        ["Older X3", "Bounded"],
        [28, 25],
        [float(b["Reference"]["cost"]), float(b["Bounded"]["cost"])],
    )
    pair(
        "matched",
        ["No book", "Luna book"],
        [24, 27],
        [
            float(cross["gpt-5.6-luna/none"]["cost"]),
            float(cross["gpt-5.6-luna/luna"]["cost"]),
        ],
    )

    evo = rows("book_evolution")
    for model, value in (("luna", 33), ("terra", 38)):
        check(
            f"{model} adaptation solves",
            sum(int(r["solves"]) for r in evo if r["model"] == model),
            value,
        )
    attr = rows("attribution")
    # The source fields are checked without importing any experiment module.
    training = [
        r
        for r in attr
        if r["stage"] == "training"
        and "terra" in r["arm"]
        and "ace" in r["arm"]
    ]
    if len(training) != 1:
        raise ValueError(
            f"Expected one Terra ACE training aggregate: {training}"
        )
    check(
        "Terra frozen train solves", float(training[0]["qualified_solves"]), 32
    )
    pair(
        "training_gap",
        ["Evolving book", "Frozen evaluation"],
        [38, 32],
        [5.998384, float(training[0]["cost"])],
    )

    prep = rows("preparation")
    pmap = {(r["model"], r["role"]): float(r["cost"]) for r in prep}
    totals = {
        m: sum(v for (model, _), v in pmap.items() if model == m)
        for m in ("luna", "terra")
    }
    check("Luna preparation known", totals["luna"], 0.91692376)
    check("Terra preparation", totals["terra"], 8.0992186)
    fig, ax = plt.subplots(figsize=(7.7, 4.6))
    fig.subplots_adjust(left=0.15, right=0.83, top=0.81, bottom=0.30)
    roles = ("generator", "reflector", "curator", "reducer")
    colors = (f"#{TEAL}", f"#{GOLD}", "6E8C9F", "C0CFD7")
    for y, model in ((1, "luna"), (0, "terra")):
        left = 0.0
        for role, color in zip(roles, colors):
            value = pmap[model, role]
            ax.barh(
                y,
                value,
                left=left,
                color=color if color.startswith("#") else "#" + color,
                height=0.48,
                label=role.title() if y == 1 else "",
            )
            left += value
        ax.text(
            totals[model] + 0.13,
            y,
            f"${totals[model]:.4f}",
            va="center",
            weight="bold",
            fontsize=19,
        )
    ax.set_yticks([1, 0], ["Luna*", "Terra"], fontsize=19)
    ax.set_xlim(0, 9.7)
    ax.set_xlabel("Recorded preparation dollars", labelpad=12)
    ax.tick_params(axis="both", length=0)
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(-0.08, -0.60),
        ncol=2,
        frameon=False,
        fontsize=14,
    )
    ax.text(
        0,
        1.55,
        "Generation is the largest component",
        fontsize=16,
        weight="bold",
    )
    save(fig, "preparation")

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.1), sharey=True)
    fig.subplots_adjust(
        left=0.07, right=0.98, top=0.82, bottom=0.20, wspace=0.22
    )
    cum = rows("cumulative_curves")
    for ax, model in zip(axes, ("luna", "terra")):
        for book, color, label in (
            ("none", f"#{MUTED}", "No book"),
            (model, f"#{TEAL}" if model == "luna" else f"#{GOLD}", "Own book"),
        ):
            rr = sorted(
                (
                    r
                    for r in cum
                    if r["model"] == f"gpt-5.6-{model}" and r["book"] == book
                ),
                key=lambda r: int(r["index"]),
            )
            assert len(rr) == 41
            x, y = (
                [float(r["spend"]) for r in rr],
                [int(r["solves"]) for r in rr],
            )
            check(
                f"{model}/{book} cumulative cost",
                x[-1],
                float(cross[f"gpt-5.6-{model}/{book}"]["cost"]),
            )
            check(
                f"{model}/{book} cumulative solves",
                y[-1],
                float(cross[f"gpt-5.6-{model}/{book}"]["qualified_solves"]),
            )
            assert all(
                x[i] <= x[i + 1] and y[i] <= y[i + 1] for i in range(40)
            )
            ax.step(
                x, y, where="post", color=color, linewidth=2.4, label=label
            )
            ax.scatter(x[-1], y[-1], color=color, s=55, zorder=5)
        ax.set_ylim(0, 40)
        ax.set_title(
            f"{model.title()} · ${0.1 if model == 'luna' else 1:.2f} / problem",
            loc="left",
            fontsize=18,
            pad=15,
        )
        ax.set_xlabel("Cumulative recorded dollars", fontsize=14, labelpad=9)
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:.1f}"))
        ax.grid(axis="y", color=f"#{LINE}", linewidth=0.8)
        ax.tick_params(length=0)
        ax.legend(loc="lower right", frameon=False, fontsize=13)
    axes[0].set_ylabel("Qualified solves / 40", fontsize=14)
    save(fig, "spend")

    luna_none, luna_own = (
        cross["gpt-5.6-luna/none"],
        cross["gpt-5.6-luna/luna"],
    )
    check(
        "Luna uncached percentage",
        round(
            100
            * (
                float(luna_own["uncached_cost"])
                / float(luna_none["uncached_cost"])
                - 1
            ),
            2,
        ),
        1.45,
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.7, 4.5))
    fig.subplots_adjust(
        left=0.04, right=0.98, top=0.73, bottom=0.15, wspace=0.28
    )
    for ax, field, title, outcome in zip(
        axes,
        ("cost", "uncached_cost"),
        ("Recorded tariff", "No cache discount"),
        ("ACE −14.1%", "ACE +1.45%"),
    ):
        vals = [float(r[field]) for r in (luna_none, luna_own)]
        ax.bar([0, 1], vals, width=0.59, color=[f"#{MUTED}", f"#{TEAL}"])
        ax.set_xticks([0, 1], ["No book", "Luna book"], fontsize=13)
        ax.set_ylim(0, 1.78)
        ax.set_yticks([])
        ax.tick_params(length=0)
        ax.set_title(title + "\n" + outcome, fontsize=15, pad=18)
        for x, v in enumerate(vals):
            ax.text(
                x,
                v + 0.055,
                f"${v:.4f}",
                ha="center",
                fontsize=14,
                weight="bold",
            )
    save(fig, "cache")

    history = rows("historical_matrix")
    fig, ax = plt.subplots(figsize=(12, 4.25))
    fig.subplots_adjust(left=0.23, right=0.92, top=0.97, bottom=0.14)
    for i, r in enumerate(reversed(history)):
        value = int(r["qualified"])
        col = (
            f"#{TEAL}" if r["label"] in ("X3", "No reflector") else f"#{MUTED}"
        )
        ax.barh(i, value, color=col, height=0.64)
        ax.text(
            value + 0.65,
            i,
            str(value),
            va="center",
            fontsize=12,
            weight="bold",
        )
    ax.set_yticks(
        range(len(history)),
        [r["label"] for r in reversed(history)],
        fontsize=12,
    )
    ax.set_xlim(0, 80)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("Qualified cells / 80", fontsize=13)
    ax.tick_params(length=0)
    save(fig, "historical")


def table(c: Canvas, slide: dict[str, Any]) -> None:
    columns, values = slide["columns"], slide["rows"]
    widths = slide["widths"]
    widths = [w * 12.1 / sum(widths) for w in widths]
    bullets = slide.get("bullets", [])
    n = len(values)
    height = 3.35 if bullets else 4.65
    if n <= 3:
        height = 2.9
    header_h = 0.68
    row_h = (height - header_h) / n
    y = 1.72
    x = 0.62
    c.shape(x, y, 12.1, header_h, NAVY, radius=True)
    for title, w in zip(columns, widths):
        c.text(
            x + 0.12,
            y + 0.09,
            w - 0.24,
            0.51,
            title,
            14.5,
            WHITE,
            True,
            minimum=13,
        )
        x += w
    y += header_h
    for i, row in enumerate(values):
        x = 0.62
        c.shape(
            x,
            y,
            12.1,
            row_h - 0.035,
            WHITE if i % 2 == 0 else "EDF1F1",
            radius=True,
        )
        for cell, w in zip(row, widths):
            size = slide.get("font", 19)
            c.text(
                x + 0.12,
                y + 0.055,
                w - 0.24,
                row_h - 0.105,
                cell,
                size,
                minimum=min(size, 15.5),
                gap=0,
            )
            x += w
        y += row_h
    if bullets:
        top = 1.72 + height + 0.20
        c.text(
            0.83,
            top,
            11.7,
            6.47 - top,
            bullets,
            20,
            bullet=True,
            minimum=18,
            gap=6,
        )


def render(
    c: Canvas, s: dict[str, Any], number: int, total_main: int, rels: list[str]
) -> None:
    layout = s["layout"]
    cover = layout == "cover"
    c.shape(0, 0, W, H, NAVY if cover else BG)
    c.shape(0.62, 0.32, 0.42, 0.055, GOLD if cover else TEAL)
    c.text(
        1.17,
        0.23,
        10.7,
        0.25,
        f"OMPHALOS  /  {s['section'].upper()}",
        10.5,
        "BCD0D6" if cover else MUTED,
    )
    if not cover:
        c.text(0.62, 0.67, 12.05, 0.9, s["title"], 30, NAVY, True, minimum=27)
    footer_color = "BCD0D6" if cover else MUTED
    c.text(
        0.62,
        7.22,
        10,
        0.18,
        "Delphyne · Development evidence · 13 September 2026",
        9,
        footer_color,
    )
    tag = f"B{number - total_main:02d}" if s.get("backup") else f"{number:02d}"
    c.text(11.7, 7.17, 1.0, 0.25, tag, 12, footer_color, True, align="r")
    c.shape(0.62, 7.02, 12.1, 0.013, "375262" if cover else LINE)
    c.text(
        0.62,
        6.57,
        12.1,
        0.43,
        s["takeaway"],
        14.5,
        "E8C38D" if cover else TEAL,
        True,
        minimum=12.5,
    )
    if cover:
        c.text(0.66, 1.12, 11.6, 1.27, s["title"], 40, WHITE, True, minimum=37)
        c.text(0.70, 2.53, 11.5, 0.43, s["subtitle"], 20, "BCD0D6")
        for i, card in enumerate(s["cards"]):
            x = 0.66 + i * 4.12
            c.shape(x, 3.25, 3.85, 2.10, "233F50", True)
            c.text(
                x + 0.20, 3.45, 3.45, 0.69, card["value"], 35, "E8C38D", True
            )
            c.text(
                x + 0.20, 4.17, 3.45, 0.36, card["label"], 17.5, WHITE, True
            )
            c.text(
                x + 0.20,
                4.64,
                3.45,
                0.59,
                card["text"],
                14,
                "E0E8E9",
                minimum=13,
            )
        c.text(
            0.78,
            5.63,
            11.8,
            0.73,
            s["bullets"],
            18,
            WHITE,
            bullet=True,
            gap=5,
            minimum=17,
        )
    elif layout == "cards":
        for i, card in enumerate(s["cards"]):
            x, y = 0.62 + (i % 2) * 6.20, 1.72 + (i // 2) * 2.43
            c.shape(x, y, 5.90, 2.26, WHITE, True, LINE)
            c.shape(x, y + 0.20, 0.055, 0.41, TEAL if i % 2 == 0 else GOLD)
            c.text(
                x + 0.23,
                y + 0.18,
                5.44,
                0.48,
                card["title"],
                20,
                TEAL if i % 2 == 0 else NAVY,
                True,
                minimum=18,
            )
            c.text(
                x + 0.23,
                y + 0.70,
                5.40,
                1.48,
                card["bullets"],
                19,
                bullet=True,
                minimum=17.5,
                gap=7,
            )
    elif layout == "pipeline":
        for i, (title, body) in enumerate(s["stages"]):
            x, y = 0.70 + (i % 3) * 4.18, 1.76 + (i // 3) * 1.63
            c.shape(x, y, 3.76, 1.37, WHITE, True, LINE)
            c.text(
                x + 0.18, y + 0.12, 0.41, 0.40, f"{i + 1:02d}", 19, TEAL, True
            )
            c.text(x + 0.71, y + 0.12, 2.85, 0.42, title, 21, NAVY, True)
            c.text(x + 0.71, y + 0.66, 2.85, 0.59, body, 17, minimum=16)
            if i % 3 < 2:
                c.text(x + 3.83, y + 0.51, 0.32, 0.38, "→", 24, TEAL)
        c.text(
            0.85,
            5.17,
            11.7,
            1.18,
            s["bullets"],
            19,
            bullet=True,
            minimum=18,
            gap=7,
        )
    elif layout in ("table", "cross_table"):
        if layout == "cross_table":
            values: list[list[str]] = []
            data = {r["arm"]: r for r in rows("crossover")}
            for model in ("luna", "terra"):
                for book in ("none", "luna", "terra"):
                    r = data[f"gpt-5.6-{model}/{book}"]
                    values.append(
                        [
                            model.title(),
                            book.title(),
                            f"**{r['qualified_solves']}/40**",
                            f"${float(r['cost']):.6f}",
                            f"${float(r['cost_per_solve']):.6f}",
                        ]
                    )
            s = {
                **s,
                "columns": [
                    "Solver",
                    "Book",
                    "Solves",
                    "Panel bill",
                    "Bill / solve",
                ],
                "widths": [2, 2, 2, 3, 3],
                "rows": values,
                "font": 20,
            }
        table(c, s)
    elif layout in ("chart", "chart_wide"):
        assert len(rels) == 1
        path = FIG / f"{s['chart']}.png"
        if layout == "chart":
            c.image(rels[0], path, 0.50, 1.77, 7.05, 4.62)
            c.shape(7.65, 1.81, 0.025, 4.44, LINE)
            c.text(
                7.98,
                1.91,
                4.61,
                4.37,
                s["bullets"],
                21,
                bullet=True,
                minimum=19.5,
                gap=12,
            )
        else:
            c.image(rels[0], path, 0.65, 1.66, 12.0, 3.89)
            c.text(
                0.85,
                5.57,
                11.7,
                0.86,
                s["bullets"],
                17.5,
                bullet=True,
                minimum=16.5,
                gap=5,
            )
    elif layout == "crossover":
        data = {r["arm"]: r for r in rows("crossover")}
        for col, label in enumerate(("No book", "Luna book", "Terra book")):
            c.text(
                3.28 + col * 3.16,
                1.73,
                2.89,
                0.4,
                label,
                20,
                NAVY,
                True,
                align="ctr",
            )
        for row, model in enumerate(("luna", "terra")):
            y = 2.26 + row * 1.34
            c.text(
                0.71,
                y + 0.13,
                2.2,
                0.40,
                model.title() + " solver",
                21,
                TEAL if model == "luna" else GOLD,
                True,
            )
            c.text(
                0.71,
                y + 0.69,
                2.2,
                0.36,
                f"${0.1 if model == 'luna' else 1:.2f} cap",
                17,
                MUTED,
            )
            for col, book in enumerate(("none", "luna", "terra")):
                r = data[f"gpt-5.6-{model}/{book}"]
                x = 3.19 + col * 3.16
                c.shape(
                    x,
                    y,
                    3.01,
                    1.18,
                    PALE if model == book else WHITE,
                    True,
                    LINE,
                )
                c.text(
                    x + 0.12,
                    y + 0.14,
                    2.77,
                    0.52,
                    f"{r['qualified_solves']} / 40",
                    30,
                    NAVY,
                    True,
                    align="ctr",
                )
                c.text(
                    x + 0.12,
                    y + 0.78,
                    2.77,
                    0.31,
                    f"${float(r['cost']):.4f}",
                    17,
                    MUTED,
                    align="ctr",
                )
        c.text(
            0.86,
            5.24,
            11.7,
            1.13,
            s["bullets"],
            20,
            bullet=True,
            minimum=18.5,
            gap=3,
        )
    elif layout == "continuation":
        rr = {(r["arm"], int(r["level"])): r for r in rows("continuations")}
        heads = ["Original allowance", "2× money", "Also 2× requests / time"]
        for i, text in enumerate(heads):
            c.text(
                3.23 + i * 3.16,
                1.75,
                2.98,
                0.54,
                text,
                18,
                NAVY,
                True,
                align="ctr",
                minimum=17,
            )
        for i, (model, arm, label) in enumerate(
            (
                ("luna", "C", "Luna · no ACE"),
                ("luna", "E", "Luna · book*"),
                ("terra", "C", "Terra · no ACE"),
                ("terra", "E", "Terra · book*"),
            )
        ):
            y = 2.46 + i * 0.57
            c.text(
                0.70, y + 0.11, 2.44, 0.39, label, 17, bold=True, minimum=16
            )
            for level in range(3):
                r = rr[f"gpt-5.6-{model}/{arm}", level]
                x = 3.21 + level * 3.16
                c.shape(
                    x,
                    y,
                    3.00,
                    0.50,
                    PALE if level and model == "terra" else WHITE,
                    True,
                )
                c.text(
                    x + 0.12,
                    y + 0.09,
                    2.76,
                    0.37,
                    f"{r['qualified_solves']} / 8",
                    21,
                    TEAL if level and model == "terra" else NAVY,
                    True,
                    align="ctr",
                )
        c.text(
            0.77,
            4.87,
            11.8,
            0.49,
            "Caps: Luna $0.10 → $0.20 → $0.20; Terra $1 → $2 → $2.  *Corrected own-book context.",
            15.5,
            MUTED,
        )
        c.text(
            0.84,
            5.39,
            11.75,
            1.04,
            s["bullets"],
            17.5,
            bullet=True,
            minimum=16.5,
            gap=5,
        )
    elif layout == "admission":
        for i, (value, label, color) in enumerate(
            (
                ("$0.085742", "Remaining balance", TEAL),
                ("$0.086368", "Required reservation", GOLD),
                ("DENIED", "$0.000626 over balance", RED),
            )
        ):
            x = 0.72 + i * 4.15
            c.shape(x, 2.01, 3.82, 1.76, WHITE, True, LINE)
            c.text(
                x + 0.17, 2.29, 3.48, 0.62, value, 31, color, True, align="ctr"
            )
            c.text(x + 0.17, 3.11, 3.48, 0.38, label, 16.5, MUTED, align="ctr")
        c.text(
            0.87,
            4.23,
            11.7,
            2.07,
            s["bullets"],
            23,
            bullet=True,
            minimum=21,
            gap=16,
        )
    else:
        raise ValueError(layout)


def visible_markdown(slides: list[dict[str, Any]]) -> None:
    parts = [
        "<!-- Generated from advisor_deck.yaml by build_advisor_deck.py. -->\n"
    ]
    cross = {r["arm"]: r for r in rows("crossover")}
    cont = {(r["arm"], int(r["level"])): r for r in rows("continuations")}
    for i, s in enumerate(slides, 1):
        text = [f"# {i:02d} · {s['title']}", f"*{s['section']}*"]
        if s.get("subtitle"):
            text.append(s["subtitle"])
        for card in s.get("cards", []):
            text.append(f"**{card.get('title', card.get('value', ''))}**")
            if "label" in card:
                text.append(f"- **{card['label']}**: {card['text']}")
            text += ["- " + b for b in card.get("bullets", [])]
        for title, body in s.get("stages", []):
            text.append(f"- **{title}:** {body.replace(chr(92) + 'n', ' ')}")
        if s.get("columns"):
            text += [
                "| " + " | ".join(s["columns"]) + " |",
                "| " + " | ".join("---" for _ in s["columns"]) + " |",
            ]
            text += ["| " + " | ".join(row) + " |" for row in s["rows"]]
        if s["layout"] in ("crossover", "cross_table"):
            text += [
                "| Solver / book | Solves / 40 | Cost | Cap |",
                "| --- | ---: | ---: | ---: |",
            ]
            for r in cross.values():
                text.append(
                    f"| {r['arm']} | {r['qualified_solves']} | ${float(r['cost']):.6f} | ${float(r['cap']):.2f} |"
                )
        if s["layout"] == "continuation":
            for model in ("luna", "terra"):
                for arm in ("C", "E"):
                    vals = [
                        cont[f"gpt-5.6-{model}/{arm}", level][
                            "qualified_solves"
                        ]
                        for level in range(3)
                    ]
                    text.append(
                        f"- {model.title()} / {arm}: {' → '.join(vals)} solves / 8."
                    )
        if s.get("chart"):
            text.append(f"![Observed data](advisor_figures/{s['chart']}.png)")
        text += ["- " + b for b in s.get("bullets", [])]
        text += ["> " + s["takeaway"], "::: notes\n" + s["notes"] + "\n:::"]
        parts.append("\n\n".join(text))
    (OUT / "advisor_slides.md").write_text("\n\n".join(parts) + "\n")


def pptx(slides: list[dict[str, Any]]) -> None:
    seed = BUILD / "seed.md"
    seed.write_text(
        "\n\n".join(
            f"# {s['title']}\n\n"
            + (
                f"![]({FIG / (s['chart'] + '.png')})"
                if s.get("chart")
                else "Placeholder."
            )
            + f"\n\n::: notes\n{s['notes']}\n:::"
            for s in slides
        )
        + "\n"
    )
    raw = BUILD / "seed.pptx"
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
        check=True,
        cwd=OUT,
    )
    with zipfile.ZipFile(raw) as z:
        parts = {name: z.read(name) for name in z.namelist()}
    names = [n for n in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    assert len(names) == len(slides)
    pres = ET.fromstring(parts["ppt/presentation.xml"])
    dims = pres.find("p:sldSz", NS)
    assert dims is not None
    dims.attrib.update(cx=u(W), cy=u(H), type="screen16x9")
    parts["ppt/presentation.xml"] = ET.tostring(
        pres, encoding="utf-8", xml_declaration=True
    )
    total_main = sum(not s.get("backup") for s in slides)
    for i, s in enumerate(slides, 1):
        name = f"ppt/slides/slide{i}.xml"
        root = ET.fromstring(parts[name])
        common = root.find("p:cSld", NS)
        assert common is not None
        tree = common.find("p:spTree", NS)
        assert tree is not None
        rels = [
            el.attrib[f"{{{NS['r']}}}embed"]
            for el in tree.findall(".//a:blip", NS)
        ]
        for child in list(tree)[2:]:
            tree.remove(child)
        render(Canvas(tree, i), s, i, total_main, rels)
        parts[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if OVERFLOWS:
        raise ValueError("\n".join(OVERFLOWS))
    # Give PowerPoint an explicit deck title and slide count.
    app = ET.fromstring(parts["docProps/app.xml"])
    for el in app.iter():
        if el.tag.endswith("}Slides"):
            el.text = str(len(slides))
    parts["docProps/app.xml"] = ET.tostring(
        app, encoding="utf-8", xml_declaration=True
    )
    with zipfile.ZipFile(
        OUT / "advisor_slides.pptx", "w", zipfile.ZIP_DEFLATED
    ) as z:
        for name, content in parts.items():
            z.writestr(name, content)
    (BUILD / "layout.json").write_text(json.dumps(LAYOUT, indent=2) + "\n")


def rehearsal(slides: list[dict[str, Any]]) -> None:
    selected = [1, 3, 4, 9, 10, 11, 13, 14, 15, 16, 19, 20, 21, 22, 24]
    text = [
        "# Advisor presentation · rehearsal guide",
        "",
        "The PowerPoint contains 24 main slides and seven backups. Every essential answer is visible on a slide. Speaker notes add nuance; file visits are optional.",
        "",
        "## A 15–20 minute route",
        "",
        "Use slides **"
        + ", ".join(map(str, selected))
        + "**. Keep the complete history tables and the exact-cost backups available for discussion. Do not rush all 31 slides into fifteen minutes.",
        "",
        "## A complete discussion",
        "",
        "Allow roughly 30–40 minutes for slides 1–24, including questions. Backup titles state the question they answer.",
        "",
        "## Before opening the code",
        "",
        "- All paths below are relative to `examples/omphalos/`.",
        "- Use symbol search; another session is working on runtime code, so line numbers may move.",
        "- Do not run an experiment, a benchmark loader, or a global test command during the presentation.",
        "",
        "## Optional visits",
        "",
        "1. `prove_ace.py`: `prove_theorem_ace`, `reflect_on_trajectory`, `curate_playbook`, `aggregate_curation_deltas`.",
        "2. `ace/ace_playbook.py`: `merge` and `refine`; `ace/ace_store.py`: `PlaybookStore.put`.",
        "3. `experiments/campaigns/ace_attribution_20260912/RESULTS.md`: search `Generator solves` and `evolving adaptation` for 38/40 and the controller caveat.",
        "4. `runtime/campaign_budget.py`: `CampaignResponsesModel.estimate_budget` and `Ledger.reserve`.",
        "5. `report/ace_retrospective/data/creator_terminal_evidence.json`: entry 0, `final_check`, `last_tactic`, `final_tactic_visible`.",
        "",
        "## Keep these distinctions explicit",
        "",
        "- 38/40 is evolving-book training generation; 32/40 is frozen-book training evaluation; 30/40 is validation.",
        "- The six-solve training gap has several changed conditions. It is not six causally attributed admission failures.",
        "- X3 28/40 in the original bounded campaign is a different reference from the later 27/40 flagship.",
        "- Historical 80-cell results are two replicate identifiers on forty problems, not eighty independent problems.",
        "- The 13 September resource-completion cycle is complete. The other active session is not assigned results here.",
        "",
        "\\newpage",
        "",
        "## Slide-by-slide cues",
        "",
    ]
    for i, s in enumerate(slides, 1):
        text += [
            f"### {i:02d} · {s['title']}",
            "",
            "- " + s["takeaway"],
            "",
            s["notes"],
            "",
        ]
    path = OUT / "advisor_rehearsal.md"
    path.write_text("\n".join(text).rstrip() + "\n")
    subprocess.run(
        [
            "pandoc",
            str(path),
            "--pdf-engine=xelatex",
            "-V",
            "mainfont=DejaVu Sans",
            "-V",
            "monofont=DejaVu Sans Mono",
            "-V",
            "fontsize=10pt",
            "-V",
            "geometry:margin=20mm",
            "-V",
            "colorlinks=true",
            "-o",
            str(OUT / "advisor_rehearsal.pdf"),
        ],
        check=True,
        cwd=OUT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def export_pdf() -> None:
    subprocess.run(
        [
            "libreoffice",
            f"-env:UserInstallation={(BUILD / 'lo-profile').as_uri()}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(BUILD),
            str(OUT / "advisor_slides.pptx"),
        ],
        check=True,
        timeout=90,
    )
    result = BUILD / "advisor_slides.pdf"
    if not result.exists():
        raise RuntimeError("LibreOffice did not export the slide PDF")
    (OUT / "advisor_slides.pdf").write_bytes(result.read_bytes())


def verify(slides: list[dict[str, Any]], pdf_done: bool) -> None:
    with zipfile.ZipFile(OUT / "advisor_slides.pptx") as z:
        assert z.testzip() is None
        notes = [
            n
            for n in z.namelist()
            if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)
        ]
        assert len(notes) == len(slides)
        for i, slide in enumerate(slides, 1):
            xml = ET.fromstring(z.read(f"ppt/slides/slide{i}.xml"))
            assert any(r.get("b") == "1" for r in xml.findall(".//a:rPr", NS))
            content = " ".join(
                el.text or "" for el in xml.findall(".//a:t", NS)
            )
            assert clean(slide["title"]) in content
    if pdf_done:
        info = subprocess.check_output(
            ["pdfinfo", str(OUT / "advisor_slides.pdf")], text=True
        )
        count = re.search(r"Pages:\s+(\d+)", info)
        assert count and int(count[1]) == len(slides)
    guard = BUILD / "preserved.json"
    preserved: dict[str, str] = (
        json.loads(guard.read_text()) if guard.exists() else {}
    )
    unchanged = {
        name: sha(OUT / name) == digest for name, digest in preserved.items()
    }
    # Another session may independently revise report.md. Record it, never revert it.
    immutable = (
        "reader_brief.md",
        "reader_brief.pdf",
        "report.pdf",
        "chart_data.xlsx",
        "next_session_prompt.md",
    )
    assert all(unchanged.get(name, True) for name in immutable)
    deliverables = [
        "advisor_deck.yaml",
        "advisor_slides.md",
        "advisor_slides.pptx",
        "advisor_rehearsal.md",
        "advisor_rehearsal.pdf",
        "build_advisor_deck.py",
    ]
    if pdf_done:
        deliverables.append("advisor_slides.pdf")
    deliverables += [str(p.relative_to(OUT)) for p in sorted(FIG.glob("*"))]
    report = dict(
        edited="2026-09-13",
        main_slides=sum(not s.get("backup") for s in slides),
        backup_slides=sum(bool(s.get("backup")) for s in slides),
        notes_slides=len(notes),
        numerical_checks=CHECKS,
        input_sha256=INPUTS,
        artifact_sha256={name: sha(OUT / name) for name in deliverables},
        untouched_document_comparison=unchanged,
        slide_pdf_export="completed" if pdf_done else "deferred",
        visual_review="Pending rendered slide review",
        runtime_code_edited=False,
        no_experiments=True,
        no_benchmark_imports=True,
        closed_data_accessed=False,
        source_scope="Audited development CSVs and completed resource-completion summary; no active experiment or runtime modules imported.",
    )
    (OUT / "advisor_verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        f"Deck: {len(slides)} slides; {len(notes)} notes; {len(CHECKS)} numerical checks; PDF {'ready' if pdf_done else 'deferred'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defer-slide-pdf", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(exist_ok=True)
    data = yaml.safe_load(remember(OUT / "advisor_deck.yaml").read_text())
    slides = data["slides"]
    assert len(slides) == 31
    assert sum(bool(s.get("backup")) for s in slides) == 7
    for filename in ("RESULTS.md", "selection.json"):
        remember(
            ROOT
            / "experiments/campaigns/resource_completion_20260913"
            / filename
        )
    selection = json.loads(
        (
            ROOT
            / "experiments/campaigns/resource_completion_20260913/selection.json"
        ).read_text()
    )
    assert selection["winner"] is None
    charts()
    if not args.verify_only:
        pptx(slides)
        visible_markdown(slides)
        rehearsal(slides)
        if not args.defer_slide_pdf:
            export_pdf()
    verify(slides, not args.defer_slide_pdf)


if __name__ == "__main__":
    main()
