"""Estilo común de gráficos (PNG estáticos para README y diapositivas).

Paleta validada (dataviz validate_palette.js, modo claro):
- categórica de 2 series: azul #2a78d6, naranja #eb6834
- ordinal bajo/medio/alto: azul 250 #86b6ef, 450 #2a78d6, 650 #104281
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_MUDA = "#898781"
GRILLA = "#e1e0d9"
EJE = "#c3c2b7"
SERIE_1 = "#2a78d6"
SERIE_2 = "#eb6834"
NEUTRO = "#c3c2b7"
RIESGO_COLOR = {"bajo": "#86b6ef", "medio": "#2a78d6", "alto": "#104281", "inválido": NEUTRO}

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "axes.edgecolor": EJE,
    "axes.labelcolor": TINTA_2,
    "axes.titlecolor": TINTA,
    "axes.titlesize": 12,
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "xtick.color": TINTA_MUDA,
    "ytick.color": TINTA_2,
    "axes.grid": False,
    "savefig.facecolor": SUPERFICIE,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})


def limpiar_ejes(ax, grilla: str = "y"):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color(EJE)
    ax.spines["bottom"].set_color(EJE)
    ax.tick_params(length=0)
    if grilla:
        ax.grid(axis=grilla, color=GRILLA, linewidth=0.8)
        ax.set_axisbelow(True)


def _aspecto(ax):
    """Unidades de datos por píxel (y/x) para redondear sin deformar."""
    fig = ax.figure
    fig.canvas.draw()
    bbox = ax.get_window_extent()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    return (abs(y1 - y0) / bbox.height) / (abs(x1 - x0) / bbox.width)


def barras(ax, posiciones, valores, grosor, color, horizontal=False, base=0.0, radio_px=4):
    """Barras con extremo de dato redondeado (4 px) y base recta.

    Llamar después de fijar los límites de los ejes.
    """
    asp = _aspecto(ax)
    fig_w = ax.get_window_extent().width
    x0, x1 = ax.get_xlim()
    px_x = abs(x1 - x0) / fig_w  # unidades x por píxel
    px_y = px_x * asp
    for p, v in zip(posiciones, valores):
        if v == 0:
            continue
        if horizontal:
            x, y, w, h = base, p - grosor / 2, v, grosor
            r = min(radio_px * px_x, abs(w) / 2)
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                        mutation_aspect=asp, linewidth=0, facecolor=color))
            ax.add_patch(Rectangle((x, y), min(abs(w), r * 1.2), h, linewidth=0, facecolor=color))
        else:
            x, y, w, h = p - grosor / 2, base, grosor, v
            r = min(radio_px * px_x, grosor / 2)
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                        mutation_aspect=asp, linewidth=0, facecolor=color))
            ax.add_patch(Rectangle((x, y), w, min(abs(h), r * asp * 1.2), linewidth=0, facecolor=color))


def leyenda(ax, items, loc="upper right"):
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=c, label=l) for l, c in items]
    leg = ax.legend(handles=handles, loc=loc, frameon=False, fontsize=9, labelcolor=TINTA_2,
                    handlelength=1.0, handleheight=1.0)
    return leg
