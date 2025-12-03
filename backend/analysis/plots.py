"""Функции построения графиков калибровки и селективного предсказания."""

from __future__ import annotations

from typing import Iterable, Sequence

from backend.grading.types import ReliabilityBin


def _require_matplotlib():
    try:
        import matplotlib  # noqa: F401
    except ImportError as exc:
        raise ImportError("Для построения графиков нужен matplotlib. Установите его: `pip install matplotlib`.") from exc


def plot_reliability_diagram(bins: Sequence[ReliabilityBin], ax=None):
    _require_matplotlib()
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))

    centers = [(b.lower + b.upper) / 2 for b in bins]
    accuracies = [b.avg_accuracy for b in bins]
    counts = [b.count for b in bins]

    ax.bar(
        centers,
        accuracies,
        width=1 / len(bins),
        color="#4f83cc",
        alpha=0.8,
        edgecolor="black",
        label="Эмпирическая точность",
    )
    ax.plot([0, 1], [0, 1], "--", color="#888888", label="Идеальная калибровка")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Уверенность")
    ax.set_ylabel("Точность")
    ax.set_title("Диаграмма калибровки")
    ax.legend()
    ax.grid(alpha=0.25)

    twin = ax.twinx()
    twin.plot(centers, counts, color="#d17b0f", alpha=0.6, label="Количество")
    twin.set_ylabel("Количество в бине")
    twin.legend(loc="lower right")
    return ax
