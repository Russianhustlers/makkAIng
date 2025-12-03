"""Метрики качества и калибровки для результатов проверки."""

from __future__ import annotations

from typing import List, Sequence, Tuple

from backend.grading.types import GradingResult, ReliabilityBin


def _require_non_empty(results: Sequence[GradingResult]) -> None:
    if not results:
        raise ValueError("Передан пустой список результатов: нечего считать.")


def accuracy(results: Sequence[GradingResult]) -> float:
    _require_non_empty(results)
    correct = sum(1 for r in results if int(r["pred_score"]) == int(r["true_score"]))
    return correct / len(results)


def mae(results: Sequence[GradingResult]) -> float:
    _require_non_empty(results)
    return sum(abs(int(r["pred_score"]) - int(r["true_score"])) for r in results) / len(results)


def quadratic_weighted_kappa(results: Sequence[GradingResult]) -> float:
    """
    Вычисляет квадратическую каппу Коэна без внешних зависимостей.
    Диапазон баллов берётся [0, max_score]; если ожидаемое совпадение 0, возвращаем 1.0.
    """

    _require_non_empty(results)
    min_rating = 0
    max_rating = max(int(r["max_score"]) for r in results)
    ratings = max_rating - min_rating + 1
    denom = (ratings - 1) ** 2 or 1

    # Матрица ошибок (true x pred).
    conf_mat = [[0 for _ in range(ratings)] for _ in range(ratings)]
    for r in results:
        true_idx = int(r["true_score"]) - min_rating
        pred_idx = int(r["pred_score"]) - min_rating
        conf_mat[true_idx][pred_idx] += 1

    # Гистограммы по истинным и предсказанным баллам.
    true_hist = [sum(row) for row in conf_mat]
    pred_hist = [sum(col[i] for col in conf_mat) for i in range(ratings)]

    total = sum(true_hist)
    weight_matrix = [[((i - j) ** 2) / denom for j in range(ratings)] for i in range(ratings)]

    observed = sum(weight_matrix[i][j] * conf_mat[i][j] for i in range(ratings) for j in range(ratings))
    expected = sum(
        weight_matrix[i][j] * true_hist[i] * pred_hist[j] / total for i in range(ratings) for j in range(ratings)
    )

    if expected == 0:
        return 1.0
    return 1.0 - observed / expected


def reliability_curve(results: Sequence[GradingResult], num_bins: int = 10) -> List[ReliabilityBin]:
    _require_non_empty(results)
    if num_bins <= 0:
        raise ValueError("Число бинов должно быть положительным.")

    bins: List[ReliabilityBin] = []
    bin_edges = [i / num_bins for i in range(num_bins + 1)]
    is_correct = [int(r["pred_score"]) == int(r["true_score"]) for r in results]

    for i in range(num_bins):
        lower, upper = bin_edges[i], bin_edges[i + 1]
        bucket_items = [
            (float(results[idx]["confidence"]), is_correct[idx]) for idx in range(len(results)) if lower <= float(
                results[idx]["confidence"]
            ) < (upper if i < num_bins - 1 else upper + 1e-9)
        ]

        if not bucket_items:
            bins.append(
                ReliabilityBin(
                    lower=lower,
                    upper=upper,
                    count=0,
                    avg_confidence=0.0,
                    avg_accuracy=0.0,
                    correct=0,
                )
            )
            continue

        count = len(bucket_items)
        avg_conf = sum(item[0] for item in bucket_items) / count
        correct = sum(1 for _, flag in bucket_items if flag)
        bins.append(
            ReliabilityBin(
                lower=lower,
                upper=upper,
                count=count,
                avg_confidence=avg_conf,
                avg_accuracy=correct / count,
                correct=correct,
            )
        )
    return bins


def accuracy_at_confidence(results: Sequence[GradingResult], threshold: float) -> Tuple[float, float]:
    """
    Возвращает кортеж (accuracy, coverage) для результатов с confidence >= threshold.
    Coverage — доля оставленных примеров от общего числа.
    """

    _require_non_empty(results)
    kept = [r for r in results if float(r["confidence"]) >= threshold]
    if not kept:
        return 0.0, 0.0
    return accuracy(kept), len(kept) / len(results)
